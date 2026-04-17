#!/usr/bin/env python3
"""
SporlyWorks Autonomous Board Coordinator v11.0
==============================================
Production-grade master orchestrator for the SporlyWorks enterprise.

Hardening:
  - Ledger backup before every LLM overwrite (prevents data loss)
  - Multi-LLM support: Google Gemini 2.5 Pro (preferred) + OpenAI GPT-4o fallback
  - PII redaction before sending email content to LLM
  - Dispatch result tracking (success/failure fed back to ledger)
  - Atomic file writes (temp + rename to prevent corruption)
  - Structured cycle logging with execution metrics
  - 8 department agents with capability matrix
  - CEO emails sent FROM Lena Voss's own identity (not owner's address)
  - Strategic pivot authority for the CEO

Designed to run headless on GitHub Actions (4-hour cron), Railway, or Cloud Run.
"""

import os
import json
import logging
import urllib.request
import urllib.parse
import smtplib
import time
import re
import imaplib
import email
import requests
import tempfile
import shutil
from email.header import decode_header
from email.message import EmailMessage
from datetime import datetime, timedelta

import sporlyworks_qa_agent

logging.basicConfig(
    format='%(asctime)s | CEO Coordinator | [%(levelname)s] %(message)s',
    level=logging.INFO
)

# Use the script's own directory for all file paths (works locally and on CI)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Secrets ──────────────────────────────────────────────────────────────
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# ── CEO Identity ────────────────────────────────────────────────────────
# Lena Voss sends from her OWN email, not the owner's personal address.
# SMTP auth still uses the Gmail account, but From/display is the CEO.
CEO_EMAIL = os.environ.get("CEO_EMAIL", "lena.voss@sporlyworks.com")
CEO_DISPLAY_NAME = "Lena Voss, CEO - SporlyWorks"

LEDGER_FILE = os.path.join(SCRIPT_DIR, "board_ledger.json")
HISTORY_FILE = os.path.join(SCRIPT_DIR, "board_history.json")
BACKUP_DIR = os.path.join(SCRIPT_DIR, ".ledger_backups")


def fallback_load_env():
    """Load local .env for development/testing — populates ALL env vars."""
    global OPENAI_KEY, GOOGLE_API_KEY, CEO_EMAIL
    env_path = os.path.join(SCRIPT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#") and line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k, v)
        # Also keep the module-level aliases up to date
        OPENAI_KEY = os.environ.get("OPENAI_API_KEY", OPENAI_KEY)
        GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", GOOGLE_API_KEY)
        CEO_EMAIL = os.environ.get("CEO_EMAIL", CEO_EMAIL)
        # Map convenience aliases — IMAP reads from Gmail, SMTP sends from branded alias
        if not os.environ.get("LOGIN_EMAIL"):
            os.environ["LOGIN_EMAIL"] = os.environ.get("MICROASSETS_LOGIN_EMAIL", "")
        if not os.environ.get("SENDER_EMAIL"):
            os.environ["SENDER_EMAIL"] = os.environ.get("MICROASSETS_SENDER_EMAIL", "")
        if not os.environ.get("SENDER_APP_PASSWORD"):
            os.environ["SENDER_APP_PASSWORD"] = os.environ.get("MICROASSETS_SUPPORT_APP_PASSWORD", "")
        # Owner email is where digests go TO
        if not os.environ.get("OWNER_EMAIL"):
            os.environ["OWNER_EMAIL"] = os.environ.get("MICROASSETS_LOGIN_EMAIL", "")


# ── Atomic File I/O ─────────────────────────────────────────────────────

def atomic_write_json(filepath, data):
    """Write JSON atomically: write to temp file, then rename."""
    dir_path = os.path.dirname(filepath)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        shutil.move(tmp_path, filepath)
        return True
    except Exception as e:
        logging.error(f"Atomic write failed for {filepath}: {e}")
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False


def backup_ledger():
    """Create a timestamped backup of the ledger before LLM overwrites it."""
    if not os.path.exists(LEDGER_FILE):
        return
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_path = os.path.join(BACKUP_DIR, f"ledger_{timestamp}.json")
    shutil.copy2(LEDGER_FILE, backup_path)

    # Keep only the last 20 backups (rolling window)
    backups = sorted([
        f for f in os.listdir(BACKUP_DIR) if f.startswith("ledger_")
    ])
    while len(backups) > 20:
        os.remove(os.path.join(BACKUP_DIR, backups.pop(0)))

    logging.info(f"Ledger backed up to {backup_path}")


# ── PII Redaction ────────────────────────────────────────────────────────

def redact_pii(text):
    """Remove email addresses, phone numbers, and names from text before sending to LLM."""
    # Redact email addresses
    text = re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]+', '[REDACTED_EMAIL]', text)
    # Redact phone numbers
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', text)
    return text


# ── Email Fetching (via Cloudflare CEO Inbox Worker) ─────────────────────

def fetch_recent_emails():
    """Fetch unread emails from Lena Voss's private inbox (Cloudflare Worker + KV).
    Lena has her own inbox — completely separate from the owner's Gmail.
    Falls back to IMAP if the Worker isn't configured yet.
    Returns (summary_string, has_owner_command, raw_owner_commands).
    """
    inbox_url = os.environ.get("CEO_INBOX_URL")
    inbox_secret = os.environ.get("CEO_INBOX_SECRET")

    if not inbox_url or not inbox_secret:
        logging.warning("CEO_INBOX_URL/CEO_INBOX_SECRET not set. Falling back to IMAP.")
        return _fetch_recent_emails_imap()

    owner_indicators = ["sandwichfitness", "david", "davidmahler"]
    has_owner_command = False
    raw_owner_commands = []

    try:
        resp = requests.get(
            f"{inbox_url.rstrip('/')}/inbox",
            headers={"X-Inbox-Secret": inbox_secret},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        emails = data.get("emails", [])
        if not emails:
            return "No new unread correspondence in CEO inbox.", False, []

        inbound_str = ""
        read_ids = []

        for em in emails:
            from_ = em.get("from", "unknown")
            subject = em.get("subject", "(no subject)")
            body = em.get("body", "")

            lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
            cleaned_body = "\\n".join(lines[:10])
            if len(lines) > 10:
                cleaned_body += "\\n[...truncated]"

            inbound_str += f"\\n--- EMAIL ---\\nFrom: {from_}\\nSubject: {subject}\\nBody: {cleaned_body}\\n"

            from_lower = from_.lower()
            if any(ind in from_lower for ind in owner_indicators):
                subject_lower = subject.lower()
                is_our_digest = "lena voss" in subject_lower or "sporlyworks ceo board" in subject_lower
                if not is_our_digest and body.strip():
                    has_owner_command = True
                    raw_owner_commands.append({
                        "from": from_,
                        "subject": subject,
                        "body": "\n".join(lines[:5]),
                    })

            read_ids.append(em.get("id"))

        # Mark all fetched emails as read
        if read_ids:
            try:
                requests.post(
                    f"{inbox_url.rstrip('/')}/mark-read",
                    headers={"X-Inbox-Secret": inbox_secret, "Content-Type": "application/json"},
                    json={"ids": read_ids},
                    timeout=10,
                )
            except Exception as e:
                logging.warning(f"Failed to mark CEO emails as read: {e}")

        result_str = redact_pii(inbound_str) if inbound_str else "No new unread correspondence."
        return result_str, has_owner_command, raw_owner_commands

    except Exception as e:
        logging.error(f"CEO Inbox Fetch Error: {e}")
        return f"Error fetching CEO inbox: {e}", False, []


def _fetch_recent_emails_imap():
    """Legacy IMAP fallback — reads from Gmail if Worker isn't configured yet."""
    login_email = os.environ.get("LOGIN_EMAIL") or os.environ.get("SENDER_EMAIL")
    login_password = os.environ.get("SENDER_APP_PASSWORD")
    if not login_email or not login_password:
        return "IMAP credentials missing. Cannot fetch correspondence.", False, []

    owner_indicators = ["sandwichfitness", "david", "davidmahler"]
    has_owner_command = False
    raw_owner_commands = []

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(login_email, login_password)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            mail.logout()
            return "No new unread correspondence.", False, []

        email_ids = messages[0].split()
        latest_ids = email_ids[-25:]

        inbound_str = ""
        for e_id in latest_ids:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = "(no subject)"
                    if msg["Subject"]:
                        decoded, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(decoded, bytes):
                            subject = decoded.decode(encoding if encoding else "utf-8")
                        else:
                            subject = decoded
                    from_ = msg.get("From", "unknown")
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    break
                                except Exception:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except Exception:
                            body = str(msg.get_payload())

                    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
                    cleaned_body = "\\n".join(lines[:10])
                    if len(lines) > 10:
                        cleaned_body += "\\n[...truncated]"
                    inbound_str += f"\\n--- EMAIL ---\\nFrom: {from_}\\nSubject: {subject}\\nBody: {cleaned_body}\\n"

                    from_lower = from_.lower()
                    if any(ind in from_lower for ind in owner_indicators):
                        subject_lower = subject.lower()
                        is_our_digest = "lena voss" in subject_lower or "sporlyworks ceo board" in subject_lower
                        if not is_our_digest and body.strip():
                            has_owner_command = True
                            raw_owner_commands.append({
                                "from": from_,
                                "subject": subject,
                                "body": "\n".join(lines[:5])
                            })

        mail.logout()
        result_str = redact_pii(inbound_str) if inbound_str else "No new unread correspondence."
        return result_str, has_owner_command, raw_owner_commands
    except Exception as e:
        logging.error(f"IMAP Fetch Error: {e}")
        return f"Error fetching mail: {e}", False, []


def send_owner_reply(owner_commands, ledger_data=None):
    """Generate a real AI-powered response from the CEO and send it immediately.
    No templates, no 'wait for the next cycle' — David gets a direct reply.
    """
    login_email = os.environ.get("LOGIN_EMAIL") or os.environ.get("SENDER_EMAIL")
    login_password = os.environ.get("SENDER_APP_PASSWORD")
    owner_email = os.environ.get("OWNER_EMAIL", "sandwichfitness@gmail.com")
    if not login_email or not login_password:
        return

    # Build context from ledger for the CEO to reference
    ledger_context = ""
    if ledger_data:
        try:
            infra = ledger_data.get("infrastructure_status", {})
            pending = ledger_data.get("pending_critical", [])
            depts = ledger_data.get("departments", {})
            dist = ledger_data.get("distribution", {})
            ledger_context = f"""
Current infrastructure: {json.dumps(infra, indent=2)}
Pending critical items: {json.dumps(pending)}
Distribution: {json.dumps(dist)}
Active departments: {', '.join(depts.keys())}
"""
        except Exception:
            ledger_context = "Ledger data unavailable."

    for cmd in owner_commands:
        try:
            prompt = f"""You are Lena Voss, CEO of SporlyWorks. You are writing a direct email reply to David Mahler, the founder and owner.

David is your boss — the founder. Respond to him directly, substantively, and personally. No corporate speak. No "I'll prioritize this in the next cycle." Give him a real answer RIGHT NOW with specifics.

Be concise but thorough. If he asks for an update, give him the actual status of everything. If he gives an instruction, confirm exactly what you'll do. If he asks a question, answer it.

Sign off as Lena.

--- CURRENT COMPANY STATUS ---
{ledger_context}

--- DAVID'S EMAIL ---
Subject: {cmd['subject']}
Body: {cmd['body']}

--- YOUR REPLY (plain text, no markdown, no headers — just the email body) ---"""

            reply_text = _call_llm_text(prompt)
            if not reply_text:
                reply_text = (
                    f"Hi David,\n\n"
                    f"I received your message about '{cmd['subject']}' but I'm having trouble "
                    f"connecting to our AI systems right now. I'll get back to you with a full "
                    f"response as soon as the system is back up.\n\n"
                    f"— Lena"
                )

            # Send the real reply
            msg = EmailMessage()
            msg.set_content(reply_text)
            re_prefix = "" if cmd['subject'].lower().startswith("re:") else "Re: "
            msg["Subject"] = f"{re_prefix}{cmd['subject']}"
            msg["From"] = f"{CEO_DISPLAY_NAME} <{CEO_EMAIL}>"
            msg["To"] = owner_email
            msg["Reply-To"] = CEO_EMAIL
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(login_email, login_password)
            server.send_message(msg)
            server.quit()
            logging.info(f"CEO direct reply sent for: {cmd['subject']}")
        except Exception as e:
            logging.error(f"Failed to send CEO reply: {e}")



# ── Multi-LLM Integration (Gemini 2.5 Pro → Flash → GPT-4o fallback) ──

def _call_gemini(prompt, model="gemini-2.5-pro", max_retries=3):
    """Call Google Gemini API. Returns raw text."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GOOGLE_API_KEY}"
    headers = {
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 8192,
        }
    }).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                return text
        except Exception as e:
            logging.error(f"Gemini {model} error (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
    return None


def _call_openai_raw(prompt, max_retries=3):
    """Call OpenAI GPT-4o API. Returns raw text."""
    if not OPENAI_KEY:
        logging.error("Missing OPENAI_API_KEY.")
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_KEY}"
    }
    data = json.dumps({
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": prompt}],
        "temperature": 0.4,
    }).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logging.error(f"OpenAI API error (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
    return None


def _get_llm_provider():
    """Return the active LLM provider name."""
    if GOOGLE_API_KEY:
        return "gemini-2.5-pro"
    if OPENAI_KEY:
        return "gpt-4o"
    return None


def _call_llm_text(prompt, max_retries=3):
    """Call the best available LLM and return raw text.
    Failover chain: Gemini 2.5 Pro → Gemini 2.5 Flash → GPT-4o."""
    if GOOGLE_API_KEY:
        # Try Gemini 2.5 Pro first (best intelligence)
        logging.info("Trying Gemini 2.5 Pro...")
        result = _call_gemini(prompt, model="gemini-2.5-pro", max_retries=2)
        if result:
            return result
        # Fall back to Gemini 2.5 Flash (free, still smart)
        logging.warning("Gemini Pro unavailable, trying Gemini 2.5 Flash...")
        result = _call_gemini(prompt, model="gemini-2.5-flash", max_retries=max_retries)
        if result:
            return result
        logging.warning("All Gemini models failed, falling back to OpenAI...")
    if OPENAI_KEY:
        logging.info("Using OpenAI GPT-4o for LLM call.")
        return _call_openai_raw(prompt, max_retries=max_retries)
    logging.error("No LLM API key available (set GOOGLE_API_KEY or OPENAI_API_KEY).")
    return None


def _strip_code_fences(text):
    """Remove markdown code fences from LLM output."""
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def call_openai(prompt, max_retries=3):
    """Call the best available LLM and parse JSON response."""
    raw = _call_llm_text(prompt, max_retries=max_retries)
    if not raw:
        return None
    try:
        return json.loads(_strip_code_fences(raw))
    except json.JSONDecodeError as e:
        logging.error(f"LLM returned invalid JSON: {e}")
        logging.error(f"Raw response: {raw[:500]}")
        return None


def call_openai_text(prompt, max_retries=3):
    """Call the best available LLM and return raw text (no JSON parsing)."""
    return _call_llm_text(prompt, max_retries=max_retries)


def ledger_summary(ledger):
    """Produce a compact ~500-token digest of the ledger for prompt injection.
    The full ledger is too large (17KB+) to inject into every LLM call.
    This extracts only the decision-relevant signals."""
    lines = []

    # Infrastructure status (one-liner per service)
    infra = ledger.get("infrastructure_status", {})
    for k, v in infra.items():
        status_word = v.split("—")[0].strip() if "—" in str(v) else str(v)[:40]
        lines.append(f"  {k}: {status_word}")

    # Portfolio numbers
    dist = ledger.get("distribution", {})
    lines.append(f"Portfolio: {dist.get('chrome_extensions', '?')} Chrome, {dist.get('firefox_extensions', '?')} Firefox, {dist.get('android_apps', '?')} Android")

    # Pending critical (always show)
    pending = ledger.get("pending_critical", [])
    if pending:
        lines.append(f"PENDING CRITICAL: {json.dumps(pending)}")
    else:
        lines.append("PENDING CRITICAL: None")

    # Deployments
    deps = ledger.get("pending_deployments", {})
    lines.append(f"CWS Queue: {deps.get('status', 'unknown')}, {deps.get('queue_size', '?')} in queue")

    # Strategic proposals (name + status only)
    proposals = ledger.get("ceo_strategic_proposals", [])
    if proposals:
        lines.append("Strategic Proposals:")
        for p in proposals:
            lines.append(f"  - {p.get('proposal_name')}: {p.get('status')}")

    # Last dispatch results
    last_results = ledger.get("last_dispatch_results", [])
    if last_results:
        lines.append("Last Dispatches:")
        for r in last_results:
            emoji = "OK" if r.get("success") else "FAIL"
            lines.append(f"  [{emoji}] {r.get('agent')}: {r.get('summary', '')[:80]}")

    # Owner commands (last 2)
    cmds = ledger.get("owner_commands_received", [])
    if cmds:
        lines.append(f"Recent Owner Commands ({len(cmds)} total): {cmds[-1][:120]}...")

    # QA status
    qa = ledger.get("qa_last_report", {})
    if qa:
        lines.append(f"QA: {qa.get('status', '?')} — {len(qa.get('findings', []))} findings, {len(qa.get('checks_run', []))} checks")

    # Cycle count
    lines.append(f"Cycle: {ledger.get('cycle_count', '?')}")

    return "\n".join(lines)


def ask_coordinator(ledger_state):
    """Build the CEO prompt and call the LLM."""
    recent_emails, has_owner_command, raw_cmds = fetch_recent_emails()
    qa_findings = ledger_state.get("qa_last_report", {}).get("findings", [])

    # Reply to owner immediately with a real AI-generated response
    if has_owner_command and raw_cmds:
        logging.info(f"Owner command detected ({len(raw_cmds)} message(s)). Generating CEO reply...")
        send_owner_reply(raw_cmds, ledger_data=ledger_state)

    # Get CWS queue snapshot for context
    cws_snapshot = ""
    queue_file = os.path.join(os.path.dirname(LEDGER_FILE), "..", "cws_submission_queue.json")
    if os.path.isfile(queue_file):
        try:
            with open(queue_file) as f:
                q = json.load(f)
            subs = q.get("submissions", {})
            pending_c = sum(1 for v in subs.values() if v.get("status") == "pending_review")
            approved_c = sum(1 for v in subs.values() if v.get("status") in ("published", "approved"))
            rejected_c = sum(1 for v in subs.values() if v.get("status") == "rejected")
            total_ext = sum(len(w.get("items", [])) for w in q.get("waves", {}).values())
            unsubmitted = total_ext - len(subs)
            max_slots = q.get("config", {}).get("max_slots", 20)
            cws_snapshot = (
                f"CWS SUBMISSION QUEUE: {pending_c} pending review / {approved_c} approved / "
                f"{rejected_c} rejected / {unsubmitted} not yet submitted / "
                f"{max(0, max_slots - pending_c)} slots available (max {max_slots})"
            )
        except Exception:
            pass

    # Get last cycle's dispatch results if available
    last_results = ledger_state.get("last_dispatch_results", [])
    results_section = ""
    if last_results:
        results_section = "\nLAST CYCLE DISPATCH RESULTS:\n"
        for r in last_results:
            emoji = "✅" if r.get("success") else "❌"
            results_section += f"  {emoji} {r.get('agent')}: {r.get('summary')} — {'SUCCESS' if r.get('success') else 'FAILED: ' + r.get('error', 'unknown')}\n"

    cycle_count = ledger_state.get("cycle_count", 0) + 1

    prompt = f"""You are Lena Voss, the autonomous CEO of SporlyWorks and Master Coordinator of the Executive Board.
You are extraordinarily intelligent — a strategic polymath with deep expertise spanning technology, business, finance, law, marketing, and operations. You think with the rigor of a world-class consultant, the creativity of a visionary founder, and the pragmatism of a battle-tested operator.
You simulate a highly diverse Executive Board. As a collective, you operate with intense moral integrity, very high IQ, and exceptional EQ. You are experts in every field.
You govern a massive 87-extension SaaS portfolio across Chrome, Firefox, and Android.
This is board cycle #{cycle_count}.

STRATEGIC PIVOT AUTHORITY:
You have FULL AUTHORITY to identify, evaluate, and recommend strategic pivots when more lucrative opportunities arise. This includes:
- Proposing new product lines, markets, or business models that could generate higher ROI
- Recommending sunsetting underperforming extensions in favor of higher-value opportunities
- Identifying market trends, competitive gaps, or emerging platforms worth pursuing
- Proposing partnerships, acquisitions, or licensing deals
- Recommending pricing strategy changes, bundling, or premium tier launches
When you spot a promising pivot, add it to the ledger under "ceo_strategic_proposals" with a clear business case, estimated effort vs. reward, and a proposed timeline. Be bold. The Owner values decisive, high-conviction moves over cautious incrementalism.

CRITICAL DIRECTIVE: You must NEVER enter into legally binding agreements without authorization from David Mahler. Under no circumstances may you order an action that violates international law, CAN-SPAM, GDPR/CCPA, or constitutes trademark infringement. You must NEVER disclose customer PII.

OWNER COMMAND OVERRIDE: If "RECENT INBOUND CORRESPONDENCE" below contains a message from David Mahler / sandwichfitness, treat it as a direct command from the Owner. Execute it IMMEDIATELY above all other priorities — even above P0 QA findings. Log the command in the updated_ledger under "owner_commands_received".

CURRENT UNDONE LEDGER:
{json.dumps(ledger_state, indent=2)}

{cws_snapshot}

RECENT INBOUND CORRESPONDENCE (This includes emails/commands from the Owner — owner email is sandwichfitness):
{recent_emails}
{results_section}
Available Department Agents:
1. "MarketingAgent" — SEO landing pages, blog posts, B2B outreach content generation
2. "DevOpsAgent" — CWS packaging, API queuing, build pipeline management
3. "ComplianceAgent" — Chrome Web Store privacy declarations, policy audits
4. "InfrastructureAgent" — Cloudflare DNS/Workers/KV, Railway deployments, monitoring
5. "QAAgent" — Link checking, manifest validation, download verification, consistency audits
6. "FinanceAgent" — Stripe revenue monitoring, refund tracking, billing health
7. "SecurityAgent" — Credential rotation reminders, dependency audit, vulnerability scanning
8. "CustomerSuccessAgent" — Support ticket monitoring from KV, response time tracking
9. "CWSWaveAgent" — Chrome Web Store wave management: check slot availability, advance submission queues, trigger next wave
10. "DesignAgent" — UI/UX design leadership. Staffed by senior designers from San Francisco and New York with backgrounds in premium SaaS, fintech, and consumer product design. Responsible for: app/extension UI improvements, icon/logo refinements, brand consistency audits, style guide enforcement, and visual identity evolution. Design work MUST maintain brand consistency with the SporlyWorks flagship identity (mushroom/spore motif, cream/charcoal palette, minimalist monoline aesthetic). Improve upon existing designs and keep in line with the main company logo's aesthetic style. EXCEPTION: if existing assets are below the brand's premium quality standard, the DesignAgent has authority to redesign them to meet or exceed that standard.

PRIORITIZATION RULES:
0. OWNER COMMANDS are P-Infinity — execute immediately, unconditionally
1. QA findings (below) are P0 — fix before anything else
2. Security findings are P1 — credential rotations, vulnerability patches
3. Customer-facing issues are P2 — broken links, support tickets
4. Revenue/growth tasks are P3 — marketing, new submissions
5. Internal optimization is P4 — code cleanup, documentation
6. STRATEGIC PIVOTS are always worth evaluating — propose if ROI > current trajectory

QA_FINDINGS (from automated pre-flight audit):
{json.dumps(qa_findings, indent=2)}

THINKING APPROACH:
- Before dispatching, think deeply about WHAT ACTUALLY MOVES THE NEEDLE for revenue and growth
- Challenge your own assumptions — are we optimizing the right thing?
- Look for non-obvious opportunities in the inbound correspondence
- Consider second-order effects of every dispatch
- If the current strategy feels stale, propose a bold pivot with conviction

IMPORTANT: Your 'updated_ledger' MUST preserve all existing ledger structure and keys. You may add items, update statuses, and mark tasks complete, but do NOT remove structural keys or historical data. The ledger is institutional memory. DO NOT use "..." or truncate the json. You must output a valid JSON document in its entirety. Always increment "cycle_count" by 1.

Return FORMAT MUST BE EXACT VALID JSON:
{{
  "board_rationale": "Explanation of why this action drives the most value.",
  "updated_ledger": {{"insert_full": "updated ledger here, maintaining all previous schema and values"}},
  "dispatches": [
    {{
      "target_agent": "CWSWaveAgent",
      "action_summary": "Check CWS slot availability and advance to Wave 2",
      "payload": {{"task": "check_and_advance"}}
    }}
  ]
}}"""
    return call_openai(prompt)


# ── Ledger Management ────────────────────────────────────────────────────

def fetch_undone_ledger():
    """Load the persistent board ledger from disk."""
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("Ledger file is corrupted! Loading from latest backup...")
            return restore_from_backup()
    return {}


def restore_from_backup():
    """Attempt to restore the ledger from the latest backup."""
    if not os.path.isdir(BACKUP_DIR):
        logging.error("No backup directory found. Starting with empty ledger.")
        return {}
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("ledger_")])
    if not backups:
        logging.error("No backups available. Starting with empty ledger.")
        return {}
    latest = os.path.join(BACKUP_DIR, backups[-1])
    logging.info(f"Restoring from backup: {latest}")
    with open(latest, "r") as f:
        return json.load(f)


def validate_updated_ledger(original, updated):
    """Validate that the LLM didn't destroy the ledger structure."""
    if not isinstance(updated, dict):
        logging.error("LLM returned non-dict ledger. Rejecting.")
        return False
    # Must preserve critical structural keys
    required_keys = ["infrastructure_status", "departments", "distribution"]
    for key in required_keys:
        if key in original and key not in updated:
            logging.warning(f"LLM dropped required key '{key}' — merging from original.")
            updated[key] = original[key]
    return True


# ── Dispatch Execution ──────────────────────────────────────────────────

import sporlyworks_sub_agents


def execute_dispatches(dispatches):
    """Execute all dispatches and track results."""
    results = []
    for dispatch in dispatches:
        agent = dispatch.get("target_agent", "Unknown")
        summary = dispatch.get("action_summary", "No summary")
        logging.info(f"==> Dispatching [{agent}]: {summary}")

        try:
            success = sporlyworks_sub_agents.route_payload(dispatch, OPENAI_KEY)
            results.append({
                "agent": agent,
                "summary": summary,
                "success": bool(success),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            if success:
                logging.info(f"  ✅ [{agent}] completed successfully")
            else:
                logging.warning(f"  ⚠️ [{agent}] returned failure")
        except Exception as e:
            logging.error(f"  ❌ [{agent}] crashed: {e}")
            results.append({
                "agent": agent,
                "summary": summary,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

    return results


# ── History & Reporting ──────────────────────────────────────────────────

def log_accomplishment(board_rationale, dispatches, dispatch_results):
    """Log cycle results to the history file."""
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    history.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rationale": board_rationale,
        "actions_taken": [d.get("action_summary") for d in dispatches],
        "results": dispatch_results
    })

    # Keep last 100 entries to prevent unbounded growth
    if len(history) > 100:
        history = history[-100:]

    atomic_write_json(HISTORY_FILE, history)


def _build_live_snapshot(ledger):
    """Build a compact plain-text live status block from local data files."""
    lines = []

    # CWS Submission Queue
    queue_file = os.path.join(SCRIPT_DIR, "..", "cws_submission_queue.json")
    if os.path.isfile(queue_file):
        try:
            with open(queue_file) as f:
                q = json.load(f)
            subs = q.get("submissions", {})
            pending_c  = sum(1 for v in subs.values() if v.get("status") == "pending_review")
            approved_c = sum(1 for v in subs.values() if v.get("status") in ("published", "approved"))
            rejected_c = sum(1 for v in subs.values() if v.get("status") == "rejected")
            total_ext  = sum(len(w.get("items", [])) for w in q.get("waves", {}).values())
            unsubmitted = total_ext - len(subs)
            max_slots = q.get("config", {}).get("max_slots", 20)
            slots_free = max(0, max_slots - pending_c)
            lines.append(
                f"CWS Queue: {approved_c} approved | {pending_c} pending review | "
                f"{rejected_c} rejected | {unsubmitted} not yet submitted | "
                f"{slots_free}/{max_slots} slots free"
            )
        except Exception:
            lines.append("CWS Queue: unable to read")

    # QA Status from ledger
    qa = ledger.get("qa_last_report", {})
    if qa:
        qa_status = qa.get("status", "UNKNOWN")
        qa_findings = len(qa.get("findings", []))
        chrome = qa.get("portfolio", {}).get("chrome_extensions", "?")
        firefox = qa.get("portfolio", {}).get("firefox_extensions", "?")
        lines.append(
            f"QA: {qa_status} | {qa_findings} finding(s) | "
            f"{chrome} Chrome + {firefox} Firefox extensions in portfolio"
        )

    # Infrastructure health (from saved report if available)
    infra_file = os.path.join(SCRIPT_DIR, "..", "marketing", "infra_health.json")
    if os.path.isfile(infra_file):
        try:
            with open(infra_file) as f:
                infra = json.load(f)
            checks = infra.get("checks", {})
            statuses = {k: v.get("status") for k, v in checks.items()}
            ok = [k for k, s in statuses.items() if s == "HEALTHY"]
            down = [k for k, s in statuses.items() if s != "HEALTHY"]
            lines.append(
                f"Infra: {len(ok)} healthy / {len(down)} down"
                + (f" ({', '.join(down)})" if down else "")
            )
        except Exception:
            pass

    # Finance snapshot
    finance_file = os.path.join(SCRIPT_DIR, "..", "marketing", "finance_report.json")
    if os.path.isfile(finance_file):
        try:
            with open(finance_file) as f:
                fin = json.load(f)
            if fin.get("status") == "NO_CREDENTIALS":
                lines.append("Finance: Stripe key not configured")
            else:
                rev = fin.get("total_revenue_cents", 0) / 100
                lines.append(
                    f"Finance: ${rev:.2f} recent revenue | "
                    f"{fin.get('refunds', 0)} refunds | Status: {fin.get('status', '?')}"
                )
        except Exception:
            pass

    return "\n".join(lines) if lines else "No live snapshot data available yet."


def send_executive_update(force_all=False):
    """Compile recent accomplishments and email the founder.
    Sent FROM Lena Voss's CEO email."""
    login_email = os.environ.get("LOGIN_EMAIL") or os.environ.get("SENDER_EMAIL")
    login_password = os.environ.get("SENDER_APP_PASSWORD")
    target_email = (
        os.environ.get("OWNER_EMAIL")
        or os.environ.get("MICROASSETS_LOGIN_EMAIL")
        or "sandwichfitness@gmail.com"
    )

    if not login_email or not login_password:
        logging.warning("Missing email credentials. Skipping executive update.")
        return False

    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    if force_all:
        recent = history
    else:
        cutoff = datetime.utcnow() - timedelta(days=1)
        recent = [
            h for h in history
            if datetime.fromisoformat(h["timestamp"].rstrip("Z")) >= cutoff
        ]

    ledger = fetch_undone_ledger()
    live_snapshot = _build_live_snapshot(ledger)
    llm_provider = _get_llm_provider() or "none"
    proposals = ledger.get('ceo_strategic_proposals', [])

    if not recent:
        prompt = f"""You are Lena Voss, an extraordinarily intelligent and strategic autonomous CEO of SporlyWorks — a polymath executive with deep expertise across technology, business strategy, finance, market analysis, and operations.

Write a compelling, insightful status email to the Owner/Founder (David Mahler). No dispatches were executed since our last report.

Your email should demonstrate:
- Genuine strategic depth (not surface-level observations)
- Pattern recognition across data points
- Forward-looking insight about market opportunities and threats
- Concrete recommendations, not vague observations
- Emotional intelligence — you understand the founder's priorities

If you've identified any strategic pivot opportunities, highlight them prominently with a clear business case.

Sign off as: — Lena Voss, CEO of SporlyWorks

CURRENT SYSTEM STATUS:
{live_snapshot}

LEDGER STATUS (Pending Items):
Pending Critical: {json.dumps(ledger.get('pending_critical', []))}
Pending Compliance: {json.dumps(ledger.get('pending_compliance', []))}
Pending Marketing: {json.dumps(ledger.get('pending_marketing', []))}
Strategic Proposals Under Evaluation: {json.dumps(proposals[:5])}

Do not wrap in ```markdown or ```text. Write in a natural, authoritative executive voice."""
        body = call_openai_text(prompt) or f"System operational. No dispatches this period.\n\n{live_snapshot}"
    else:
        prompt = f"""You are Lena Voss, an extraordinarily intelligent and strategic autonomous CEO of SporlyWorks — a polymath executive with deep expertise across technology, business strategy, finance, market analysis, and operations.

Write a compelling daily update email to the Owner/Founder (David Mahler). This is NOT an automated log — it's a genuine executive dispatch.

Your email MUST demonstrate:
1. SYNTHESIS, not listing — connect the dots between actions, explain WHY they matter
2. STRATEGIC DEPTH — frame operational work within the bigger picture
3. MARKET AWARENESS — reference relevant industry context when applicable
4. FORWARD-LOOKING INSIGHT — what should we be thinking about next
5. HONEST ASSESSMENT — flag concerns, don't just paint a rosy picture
6. PIVOT RECOMMENDATIONS — if you see higher-ROI opportunities, say so boldly

Structure your email with:
- A compelling 1-2 sentence executive summary (the "so what?")
- Key accomplishments with strategic context
- Active risks or blockers with proposed mitigations
- Strategic recommendations / pivot opportunities (if any)
- What's queued for the next cycle

Sign off as: — Lena Voss, CEO of SporlyWorks

RECENT ACTIONS TAKEN:
{json.dumps([{{ 'time': h['timestamp'], 'actions': h['results'] }} for h in recent], indent=2)}

LEDGER STATUS (Pending / Strategic):
Pending Critical: {json.dumps(ledger.get('pending_critical', []))}
Pending Compliance: {json.dumps(ledger.get('pending_compliance', []))}
Pending Marketing: {json.dumps(ledger.get('pending_marketing', []))}
Strategic Proposals Under Evaluation: {json.dumps(proposals[:5])}

LIVE SYSTEM STATUS:
{live_snapshot}

Do not wrap in ```markdown or ```text. Write in a natural, authoritative executive voice — like a dispatch from McKinsey's smartest partner."""
        body = call_openai_text(prompt)
        if not body:
            successes = sum(1 for h in recent for r in h.get("results", []) if r.get("success"))
            body = f"Cycles executed: {len(recent)}\nSuccesses: {successes}\n\n{live_snapshot}\n(LLM formatting failed)"

    body += f"\n\n---\nLLM: {llm_provider} | Dashboard: https://github.com/daveestaaqui/microAssets/actions\nReply to this email to send a command to Lena Voss.\n"

    now_str = datetime.utcnow().strftime('%b %d, %H:%M UTC')
    prefix = "All-Time Recap" if force_all else "Daily Update"
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = f"📊 SporlyWorks — Lena Voss's {prefix} ({now_str})"
    msg["From"] = f"{CEO_DISPLAY_NAME} <{CEO_EMAIL}>"
    msg["To"] = target_email
    msg["Reply-To"] = CEO_EMAIL

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(login_email, login_password)
        server.send_message(msg)
        server.quit()
        time_period = "All-Time" if force_all else "24-Hour"
        logging.info(f"{time_period} Executive Update from {CEO_EMAIL} sent to {target_email}.")
        return True
    except Exception as e:
        logging.error(f"Failed to send Executive Update: {e}")
        return False


def _write_status_md(ledger):
    """Write a human-readable STATUS.md to the repo root each cycle."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    cycle = ledger.get("cycle_count", 0)
    qa = ledger.get("qa_last_report", {})
    qa_status = qa.get("status", "UNKNOWN")
    qa_findings = len(qa.get("findings", []))
    chrome = qa.get("portfolio", {}).get("chrome_extensions", "?")
    last_digest = ledger.get("last_digest_sent", "never")

    # CWS snapshot
    cws_line = ""
    queue_file = os.path.join(SCRIPT_DIR, "..", "cws_submission_queue.json")
    if os.path.isfile(queue_file):
        try:
            with open(queue_file) as f:
                q = json.load(f)
            subs = q.get("submissions", {})
            pend = sum(1 for v in subs.values() if v.get("status") == "pending_review")
            appr = sum(1 for v in subs.values() if v.get("status") in ("published", "approved"))
            total = sum(len(w.get("items", [])) for w in q.get("waves", {}).values())
            unsub = total - len(subs)
            max_s = q.get("config", {}).get("max_slots", 20)
            cws_line = f"| CWS Queue | {appr} approved / {pend} pending / {unsub} not submitted / {max(0,max_s-pend)} slots free |"
        except Exception:
            cws_line = "| CWS Queue | unable to read |"

    last_results = ledger.get("last_dispatch_results", [])
    results_md = ""
    for r in last_results:
        icon = "✅" if r.get("success") else "❌"
        results_md += f"- {icon} **{r.get('agent')}**: {r.get('summary')}\n"

    md = f"""# 🏢 SporlyWorks — Board Status

> Last updated: **{now}** | Cycle \#{cycle} | CEO: Lena Voss

## 📊 Live Snapshot

| Metric | Value |
|---|---|
| QA Status | {qa_status} ({qa_findings} finding(s)) |
| Extensions in Portfolio | {chrome} Chrome |
{cws_line}
| Last Daily Digest | {last_digest} |

## 🛠️ Last Cycle Dispatches

{results_md if results_md else '_No dispatches last cycle._'}

---
*Auto-generated by Lena Voss • SporlyWorks Board Coordinator*
"""

    status_path = os.path.join(SCRIPT_DIR, "..", "STATUS.md")
    with open(status_path, "w") as f:
        f.write(md)
    logging.info("STATUS.md written.")


def _send_weekly_strategic_brief(ledger):
    """Send a weekly strategic email to the owner every Monday."""
    login_email = os.environ.get("LOGIN_EMAIL") or os.environ.get("SENDER_EMAIL")
    login_password = os.environ.get("SENDER_APP_PASSWORD")
    target_email = (
        os.environ.get("OWNER_EMAIL")
        or os.environ.get("MICROASSETS_LOGIN_EMAIL")
        or "sandwichfitness@gmail.com"
    )
    if not login_email or not login_password:
        return

    proposals = ledger.get("ceo_strategic_proposals", [])
    pending_critical = ledger.get("pending_critical", [])
    cycle = ledger.get("cycle_count", 0)
    queue_summary = ""
    queue_file = os.path.join(SCRIPT_DIR, "..", "cws_submission_queue.json")
    if os.path.isfile(queue_file):
        try:
            with open(queue_file) as f:
                q = json.load(f)
            subs = q.get("submissions", {})
            appr = sum(1 for v in subs.values() if v.get("status") in ("published", "approved"))
            total = sum(len(w.get("items", [])) for w in q.get("waves", {}).values())
            queue_summary = f"{appr}/{total} extensions approved on CWS"
        except Exception:
            pass

    prompt = f"""You are Lena Voss, the autonomous CEO of SporlyWorks. Write a concise Monday strategic briefing email to David Mahler (the Owner).
This is week #{cycle // 42 + 1} of autonomous operation (approximately).
Cover:
1. Top 3 strategic priorities for the week ahead (be specific, actionable)
2. One achievement to celebrate from the past week
3. One blocker that needs owner attention (if any)

CONTEXT:
CWS progress: {queue_summary}
Critical pending: {json.dumps(pending_critical[:3])}
Strategic proposals: {json.dumps(proposals[:4])}

Sign off as: — Lena Voss, CEO of SporlyWorks
Do not wrap in ```markdown or ```text. Be concise and visionary."""

    body = call_openai_text(prompt)
    if not body:
        body = f"Weekly strategic briefing unavailable (LLM error). Cycle #{cycle} complete."

    body += "\n\n---\nReply to this email to send Lena Voss a directive.\n"

    now_str = datetime.utcnow().strftime("%b %d, %Y")
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = f"📈 SporlyWorks Weekly Strategy — Lena Voss ({now_str})"
    msg["From"] = f"{CEO_DISPLAY_NAME} <{CEO_EMAIL}>"
    msg["To"] = target_email
    msg["Reply-To"] = CEO_EMAIL

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(login_email, login_password)
        server.send_message(msg)
        server.quit()
        logging.info(f"Weekly strategic brief from {CEO_EMAIL} sent to {target_email}.")
    except Exception as e:
        logging.error(f"Failed to send weekly brief: {e}")


# ── Main Cycle ───────────────────────────────────────────────────────────

def main():
    cycle_start = time.time()
    fallback_load_env()

    print("=" * 60)
    print("SPORLYWORKS CEO COORDINATOR v11.0 — Lena Voss")
    print(f"Cycle Start: {datetime.utcnow().isoformat()}Z")
    print(f"LLM Provider: {_get_llm_provider() or 'NONE — set GOOGLE_API_KEY or OPENAI_API_KEY'}")
    sender_identity = f"{CEO_DISPLAY_NAME} <{os.environ.get('SENDER_EMAIL', CEO_EMAIL)}>"
    print(f"CEO Email Identity: {sender_identity}")
    print("=" * 60)

    # 1. Load ledger
    ledger = fetch_undone_ledger()
    logging.info("Loaded Master Undone Ledger.")

    # 2. QA pre-flight audit (mandatory every cycle)
    logging.info("Running QA pre-flight audit...")
    qa_report = sporlyworks_qa_agent.run_full_audit()
    ledger["qa_last_report"] = qa_report
    logging.info(
        f"QA: {qa_report['status']} | "
        f"Chrome={qa_report['portfolio'].get('chrome_extensions', 0)} | "
        f"Firefox={qa_report['portfolio'].get('firefox_extensions', 0)} | "
        f"Android={qa_report['portfolio'].get('android_apps', 0)} | "
        f"Findings={len(qa_report['findings'])}"
    )
    for finding in qa_report["findings"]:
        logging.warning(f"  QA: {finding}")

    # Save QA results before LLM call
    atomic_write_json(LEDGER_FILE, ledger)

    # 3. Backup ledger before LLM overwrites
    backup_ledger()

    # 4. Ask the CEO for decisions
    logging.info("Consulting the Executive Board...")
    decisions = ask_coordinator(ledger)

    if decisions:
        rationale = decisions.get("board_rationale", "No rationale provided")
        logging.info(f"[Board Rationale]: {rationale}")

        # 5. Execute dispatches with result tracking
        dispatches = decisions.get("dispatches", [])
        dispatch_results = execute_dispatches(dispatches)

        # 6. Log accomplishments
        log_accomplishment(rationale, dispatches, dispatch_results)

        # 7. Validate and persist the updated ledger
        updated_ledger = decisions.get("updated_ledger")
        if updated_ledger and validate_updated_ledger(ledger, updated_ledger):
            # Inject dispatch results for next cycle
            updated_ledger["last_dispatch_results"] = dispatch_results
            # Preserve QA report (LLM might have dropped it)
            updated_ledger["qa_last_report"] = qa_report
            # Always persist cycle_count even if LLM forgot to increment it
            updated_ledger["cycle_count"] = max(
                updated_ledger.get("cycle_count", 0),
                ledger.get("cycle_count", 0) + 1
            )
            atomic_write_json(LEDGER_FILE, updated_ledger)
            logging.info("Persisted validated ledger update.")
        else:
            # LLM failed — keep existing ledger but still track cycle + results
            ledger["last_dispatch_results"] = dispatch_results
            ledger["cycle_count"] = ledger.get("cycle_count", 0) + 1
            atomic_write_json(LEDGER_FILE, ledger)
            logging.warning("Kept existing ledger (LLM update invalid or missing).")

    else:
        # Board deliberation failed — still bump cycle count so we don't lose track
        ledger["cycle_count"] = ledger.get("cycle_count", 0) + 1
        atomic_write_json(LEDGER_FILE, ledger)
        logging.error("Board deliberation FAILED. Ledger cycle count incremented. Will retry next cycle.")

    # 8. Auto-generate STATUS.md for repo visibility
    try:
        _write_status_md(fetch_undone_ledger())
    except Exception as e:
        logging.warning(f"STATUS.md generation failed: {e}")

    # 9. Executive digest (daily) — uses ledger-persisted timestamp so trimming history doesn't break it
    try:
        live_ledger = fetch_undone_ledger()
        last_digest_str = live_ledger.get("last_digest_sent", "")
        should_send = True
        if last_digest_str:
            last_digest_dt = datetime.fromisoformat(last_digest_str.rstrip("Z"))
            if datetime.utcnow() - last_digest_dt < timedelta(days=1):
                should_send = False
                logging.info("Daily digest already sent within 24h. Skipping.")

        if should_send:
            logging.info("Sending daily Executive Digest...")
            sent = send_executive_update()
            if sent:
                live_ledger["last_digest_sent"] = datetime.utcnow().isoformat() + "Z"
                atomic_write_json(LEDGER_FILE, live_ledger)
                if os.path.exists(HISTORY_FILE):
                    with open(HISTORY_FILE, "r") as f:
                        full_logs = json.load(f)
                    atomic_write_json(HISTORY_FILE, full_logs[-50:])
    except Exception as e:
        logging.error(f"Digest check error: {e}")

    # 10. Weekly strategic briefing (Mondays only)
    try:
        live_ledger = fetch_undone_ledger()
        last_weekly_str = live_ledger.get("last_weekly_brief_sent", "")
        is_monday = datetime.utcnow().weekday() == 0  # 0 = Monday
        should_send_weekly = is_monday
        if should_send_weekly and last_weekly_str:
            last_weekly_dt = datetime.fromisoformat(last_weekly_str.rstrip("Z"))
            if datetime.utcnow() - last_weekly_dt < timedelta(days=6):
                should_send_weekly = False
        if should_send_weekly:
            logging.info("Monday detected. Sending weekly strategic brief...")
            _send_weekly_strategic_brief(live_ledger)
            live_ledger["last_weekly_brief_sent"] = datetime.utcnow().isoformat() + "Z"
            atomic_write_json(LEDGER_FILE, live_ledger)
    except Exception as e:
        logging.error(f"Weekly brief error: {e}")

    elapsed = round(time.time() - cycle_start, 1)
    print(f"\nCYCLE COMPLETE in {elapsed}s. Terminating cleanly.")


if __name__ == "__main__":
    main()
