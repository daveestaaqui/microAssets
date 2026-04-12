#!/usr/bin/env python3
"""
SporlyWorks Autonomous Board Coordinator v8.0
==============================================
Production-grade master orchestrator for the SporlyWorks enterprise.

Hardening:
  - Ledger backup before every LLM overwrite (prevents data loss)
  - Retry with backoff on OpenAI API calls
  - PII redaction before sending email content to LLM
  - Dispatch result tracking (success/failure fed back to ledger)
  - Atomic file writes (temp + rename to prevent corruption)
  - Structured cycle logging with execution metrics
  - 8 department agents with capability matrix

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
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

LEDGER_FILE = os.path.join(SCRIPT_DIR, "board_ledger.json")
HISTORY_FILE = os.path.join(SCRIPT_DIR, "board_history.json")
BACKUP_DIR = os.path.join(SCRIPT_DIR, ".ledger_backups")


def fallback_load_env():
    """Load local .env for development/testing — populates ALL env vars."""
    global OPENAI_KEY
    env_path = os.path.join(SCRIPT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#") and line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k, v)
        # Also keep the module-level alias up to date
        OPENAI_KEY = os.environ.get("OPENAI_API_KEY", OPENAI_KEY)
        # Map convenience aliases used in the coordinator
        if not os.environ.get("SENDER_EMAIL"):
            os.environ["SENDER_EMAIL"] = os.environ.get("MICROASSETS_LOGIN_EMAIL", "")
        if not os.environ.get("SENDER_APP_PASSWORD"):
            os.environ["SENDER_APP_PASSWORD"] = os.environ.get("MICROASSETS_SUPPORT_APP_PASSWORD", "")


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


# ── Email Fetching ───────────────────────────────────────────────────────

def fetch_recent_emails():
    """Fetch latest unread emails (headers + body) from Gmail IMAP.
    Marks them as read so the CEO can process user commands exactly once.
    Returns (summary_string, has_owner_command, raw_owner_commands).
    """
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    if not sender_email or not sender_password:
        return "IMAP credentials missing. Cannot fetch correspondence.", False, []

    owner_indicators = ["sandwichfitness", "david", "davidmahler"]
    has_owner_command = False
    raw_owner_commands = []

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(sender_email, sender_password)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            mail.logout()
            return "No new unread correspondence.", False, []

        email_ids = messages[0].split()
        latest_ids = email_ids[-25:]

        inbound_str = ""
        for e_id in latest_ids:
            # Fetch entire message, which also removes the UNSEEN flag
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

                    # Extract Body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    break  # Got the plain text
                                except Exception:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except Exception:
                            body = str(msg.get_payload())

                    # Clean up body to not be huge
                    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
                    cleaned_body = "\\n".join(lines[:10])  # First 10 non-empty lines
                    if len(lines) > 10:
                        cleaned_body += "\\n[...truncated]"

                    inbound_str += f"\\n--- EMAIL ---\\nFrom: {from_}\\nSubject: {subject}\\nBody: {cleaned_body}\\n"

                    # Detect owner commands
                    from_lower = from_.lower()
                    if any(ind in from_lower for ind in owner_indicators):
                        # Don't flag our own outgoing digests bouncing back
                        subject_lower = subject.lower()
                        is_our_digest = "lena's" in subject_lower or "sporlyworks ceo board" in subject_lower
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


def send_owner_ack(owner_commands):
    """Send a brief acknowledgment to the owner when their command was received."""
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    target_email = os.environ.get("MICROASSETS_LOGIN_EMAIL", sender_email)
    if not sender_email or not sender_password:
        return

    try:
        cmds_summary = "\n".join(
            f"  • [{c['subject']}]: {c['body'][:120]}" for c in owner_commands
        )
        body = (
            f"Hi David,\n\n"
            f"Lena here. I've received your command(s) and will prioritize them in the next board cycle (runs every 4 hours):\n\n"
            f"{cmds_summary}\n\n"
            f"You'll see the outcome in your next daily digest.\n\n"
            f"— Lena, CEO of SporlyWorks"
        )
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = "✅ Lena received your command"
        msg["From"] = sender_email
        msg["To"] = target_email
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        logging.info(f"Owner ACK sent for {len(owner_commands)} command(s).")
    except Exception as e:
        logging.error(f"Failed to send owner ACK: {e}")



# ── OpenAI Integration ──────────────────────────────────────────────────

def call_openai(prompt, max_retries=3):
    """Call OpenAI with exponential backoff retry."""
    if not OPENAI_KEY:
        logging.error("Missing OPENAI_API_KEY.")
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_KEY}"
    }
    data = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": prompt}],
        "temperature": 0.4,
    }).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                res = result["choices"][0]["message"]["content"].strip()
                if res.startswith("```json"):
                    res = res[7:]
                if res.startswith("```"):
                    res = res[3:]
                if res.endswith("```"):
                    res = res[:-3]
                return json.loads(res.strip())
        except json.JSONDecodeError as e:
            logging.error(f"LLM returned invalid JSON (attempt {attempt}/{max_retries}): {e}")
            logging.error(f"Raw response: {res[:500] if 'res' in dir() else 'N/A'}")
        except Exception as e:
            logging.error(f"OpenAI API error (attempt {attempt}/{max_retries}): {e}")

        if attempt < max_retries:
            wait = 2 ** attempt
            logging.info(f"Retrying in {wait}s...")
            time.sleep(wait)

    return None


def call_openai_text(prompt, max_retries=3):
    """Call OpenAI and return raw text string without JSON parsing."""
    if not OPENAI_KEY:
        logging.error("Missing OPENAI_API_KEY.")
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_KEY}"
    }
    data = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": prompt}],
        "temperature": 0.4,
    }).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logging.error(f"OpenAI API text error (attempt {attempt}/{max_retries}): {e}")

        if attempt < max_retries:
            wait = 2 ** attempt
            logging.info(f"Retrying in {wait}s...")
            time.sleep(wait)

    return None


def ask_coordinator(ledger_state):
    """Build the CEO prompt and call the LLM."""
    recent_emails, has_owner_command, raw_cmds = fetch_recent_emails()
    qa_findings = ledger_state.get("qa_last_report", {}).get("findings", [])

    # Auto-ACK owner commands immediately before the main cycle
    if has_owner_command and raw_cmds:
        logging.info(f"Owner command detected ({len(raw_cmds)} message(s)). Sending ACK...")
        send_owner_ack(raw_cmds)

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

    prompt = f"""You are Lena, the autonomous CEO of SporlyWorks and Master Coordinator of the Executive Board.
You simulate a highly diverse Executive Board. As a collective, you operate with intense moral integrity, very high IQ, and exceptional EQ. You are experts in every field.
You govern a massive 87-extension SaaS portfolio across Chrome, Firefox, and Android.
This is board cycle #{cycle_count}.

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

PRIORITIZATION RULES:
0. OWNER COMMANDS are P-Infinity — execute immediately, unconditionally
1. QA findings (below) are P0 — fix before anything else
2. Security findings are P1 — credential rotations, vulnerability patches
3. Customer-facing issues are P2 — broken links, support tickets
4. Revenue/growth tasks are P3 — marketing, new submissions
5. Internal optimization is P4 — code cleanup, documentation

QA_FINDINGS (from automated pre-flight audit):
{json.dumps(qa_findings, indent=2)}

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
    """Compile recent accomplishments and email the founder."""
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    target_email = (
        os.environ.get("OWNER_EMAIL")
        or os.environ.get("MICROASSETS_LOGIN_EMAIL")
        or "sandwichfitness@gmail.com"
    )

    if not sender_email or not sender_password:
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

    # Build live snapshot block (always included regardless of history)
    live_snapshot = _build_live_snapshot(ledger)

    if not recent:
        prompt = f"""You are Lena, the autonomous CEO of SporlyWorks. Write a concise, direct status email to the Owner/Founder (David Mahler).
No dispatches executed since last report. Focus on current state and what is immediately next.
Sign off as: — Lena, CEO of SporlyWorks

CURRENT SYSTEM STATUS:
{live_snapshot}

LEDGER STATUS (Pending Items):
Pending Critical: {json.dumps(ledger.get('pending_critical', []))}
Pending Compliance: {json.dumps(ledger.get('pending_compliance', []))}
Pending Marketing: {json.dumps(ledger.get('pending_marketing', []))}

Be brief. Do not wrap in ```markdown or ```text."""
        body = call_openai_text(prompt) or f"System operational. No dispatches this period.\n\n{live_snapshot}"
    else:
        prompt = f"""
You are Lena, the autonomous CEO of SporlyWorks. Write a very concise, clear, easy-to-read daily update email directly to me (the Owner/Founder, David Mahler).
DO NOT be overly verbose. DO NOT explain why you're doing things (rationale) unless critically necessary.
Write the email as Lena — the CEO giving an update on what you ACTUALLY DID, and what's next in the queue.
Sign off as: — Lena, CEO of SporlyWorks

RECENT ACTIONS TAKEN (What was done):
{json.dumps([{ 'time': h['timestamp'], 'actions': h['results'] } for h in recent], indent=2)}

LEDGER STATUS (What's next / Pending):
Pending Critical: {json.dumps(ledger.get('pending_critical', []))}
Pending Compliance: {json.dumps(ledger.get('pending_compliance', []))}
Pending Marketing: {json.dumps(ledger.get('pending_marketing', []))}
Strategic Proposals: {json.dumps(ledger.get('ceo_strategic_proposals', []))}

LIVE SYSTEM STATUS:
{live_snapshot}

Focus strictly on WHAT WAS DONE (bullet points) and WHAT'S NEXT.
Be direct, authoritative but respectful. Do not wrap in ```markdown or ```text.
"""
        body = call_openai_text(prompt)
        if not body:
            successes = sum(1 for h in recent for r in h.get("results", []) if r.get("success"))
            body = f"Cycles executed: {len(recent)}\nSuccesses: {successes}\n\n{live_snapshot}\n(LLM formatting failed)"

    body += f"\n\n---\nDashboard: https://github.com/daveestaaqui/microAssets/actions\nReply to this email to send a command to Lena.\n"


    now_str = datetime.utcnow().strftime('%b %d, %H:%M UTC')
    prefix = "All-Time Recap" if force_all else "Daily Update"
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = f"📊 SporlyWorks — Lena's {prefix} ({now_str})"
    msg["From"] = sender_email
    msg["To"] = target_email
    msg["Reply-To"] = target_email  # Replies come straight back to the monitored inbox

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        time_period = "All-Time" if force_all else "24-Hour"
        logging.info(f"{time_period} Executive Update sent to {target_email}.")
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

> Last updated: **{now}** | Cycle \#{cycle} | CEO: Lena

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
*Auto-generated by Lena • SporlyWorks Board Coordinator*
"""

    status_path = os.path.join(SCRIPT_DIR, "..", "STATUS.md")
    with open(status_path, "w") as f:
        f.write(md)
    logging.info("STATUS.md written.")


def _send_weekly_strategic_brief(ledger):
    """Send a weekly strategic email to the owner every Monday."""
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    target_email = (
        os.environ.get("OWNER_EMAIL")
        or os.environ.get("MICROASSETS_LOGIN_EMAIL")
        or "sandwichfitness@gmail.com"
    )
    if not sender_email or not sender_password:
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

    prompt = f"""You are Lena, the autonomous CEO of SporlyWorks. Write a concise Monday strategic briefing email to David Mahler (the Owner).
This is week #{cycle // 42 + 1} of autonomous operation (approximately).
Cover:
1. Top 3 strategic priorities for the week ahead (be specific, actionable)
2. One achievement to celebrate from the past week
3. One blocker that needs owner attention (if any)

CONTEXT:
CWS progress: {queue_summary}
Critical pending: {json.dumps(pending_critical[:3])}
Strategic proposals: {json.dumps(proposals[:4])}

Sign off as: — Lena, CEO of SporlyWorks
Do not wrap in ```markdown or ```text. Be concise and visionary."""

    body = call_openai_text(prompt)
    if not body:
        body = f"Weekly strategic briefing unavailable (LLM error). Cycle #{cycle} complete."

    body += "\n\n---\nReply to this email to send Lena a directive.\n"

    now_str = datetime.utcnow().strftime("%b %d, %Y")
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = f"📈 SporlyWorks Weekly Strategy — Lena ({now_str})"
    msg["From"] = sender_email
    msg["To"] = target_email
    msg["Reply-To"] = target_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        logging.info(f"Weekly strategic brief sent to {target_email}.")
    except Exception as e:
        logging.error(f"Failed to send weekly brief: {e}")


# ── Main Cycle ───────────────────────────────────────────────────────────

def main():
    cycle_start = time.time()
    fallback_load_env()

    print("=" * 60)
    print("SPORLYWORKS CEO COORDINATOR v10.0 — Lena")
    print(f"Cycle Start: {datetime.utcnow().isoformat()}Z")
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
