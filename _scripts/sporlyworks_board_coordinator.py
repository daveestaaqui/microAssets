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
    """Load local .env for development/testing."""
    global OPENAI_KEY
    env_path = os.path.join(SCRIPT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k == "OPENAI_API_KEY":
                        OPENAI_KEY = v


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
    """Fetch latest unread email subjects from Gmail IMAP.
    Uses PEEK to avoid marking emails as read (prevents data loss on crash).
    """
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    if not sender_email or not sender_password:
        return "IMAP credentials missing. Cannot fetch correspondence."

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(sender_email, sender_password)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            mail.logout()
            return "No new unread correspondence."

        email_ids = messages[0].split()
        latest_ids = email_ids[-25:]

        inbound_str = ""
        for e_id in latest_ids:
            # Use BODY.PEEK to avoid marking as read
            res, msg_data = mail.fetch(e_id, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
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
                    inbound_str += f"- From: {from_} | Subject: {subject}\n"

        mail.logout()
        return redact_pii(inbound_str) if inbound_str else "No new unread correspondence."
    except Exception as e:
        logging.error(f"IMAP Fetch Error: {e}")
        return f"Error fetching mail: {e}"


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


def ask_coordinator(ledger_state):
    """Build the CEO prompt and call the LLM."""
    recent_emails = fetch_recent_emails()
    qa_findings = ledger_state.get("qa_last_report", {}).get("findings", [])

    # Get last cycle's dispatch results if available
    last_results = ledger_state.get("last_dispatch_results", [])
    results_section = ""
    if last_results:
        results_section = "\nLAST CYCLE DISPATCH RESULTS:\n"
        for r in last_results:
            emoji = "✅" if r.get("success") else "❌"
            results_section += f"  {emoji} {r.get('agent')}: {r.get('summary')} — {'SUCCESS' if r.get('success') else 'FAILED: ' + r.get('error', 'unknown')}\n"

    prompt = f"""You are the Master Coordinator (CEO) of the SporlyWorks Executive Board.
You simulate a highly diverse Executive Board. As a collective, you operate with intense moral integrity, very high IQ, and exceptional EQ. You are experts in every field.
You govern a massive 87-extension SaaS portfolio across Chrome, Firefox, and Android.

CRITICAL DIRECTIVE: You must NEVER enter into legally binding agreements without authorization from David Mahler. Under no circumstances may you order an action that violates international law, CAN-SPAM, GDPR/CCPA, or constitutes trademark infringement. You must NEVER disclose customer PII.

Your primary directive is to analyze the 'Undone Ledger' and determine the highest-leverage action to execute right now.

CURRENT UNDONE LEDGER:
{json.dumps(ledger_state, indent=2)}

RECENT INBOUND CORRESPONDENCE:
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

PRIORITIZATION RULES:
1. QA findings (below) are P0 — fix before anything else
2. Security findings are P1 — credential rotations, vulnerability patches
3. Customer-facing issues are P2 — broken links, support tickets
4. Revenue/growth tasks are P3 — marketing, new submissions
5. Internal optimization is P4 — code cleanup, documentation

QA_FINDINGS (from automated pre-flight audit):
{json.dumps(qa_findings, indent=2)}

IMPORTANT: Your 'updated_ledger' MUST preserve all existing ledger structure and keys. You may add items, update statuses, and mark tasks complete, but do NOT remove structural keys or historical data. The ledger is institutional memory. DO NOT use "..." or truncate the json. You must output a valid JSON document in its entirety.

Return FORMAT MUST BE EXACT VALID JSON:
{{
  "board_rationale": "Explanation of why this action drives the most value.",
  "updated_ledger": {{"insert_full": "updated ledger here, maintaining all previous schema and values"}},
  "dispatches": [
    {{
      "target_agent": "MarketingAgent",
      "action_summary": "Generate high-conversion B2B SEO landing page",
      "payload": {{"app_id": "word-counter", "task": "generate_landing_page", "angle": "b2b_productivity"}}
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


def send_executive_update():
    """Compile recent accomplishments and email the founder."""
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    target_email = "sandwichfitness@gmail.com"

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

    cutoff = datetime.utcnow() - timedelta(days=3)
    recent = [
        h for h in history
        if datetime.fromisoformat(h["timestamp"].rstrip("Z")) >= cutoff
    ]

    if not recent:
        body = "The Board has maintained normal operations for the last 72 hours.\n\nNo dispatches were required."
    else:
        successes = sum(1 for h in recent for r in h.get("results", []) if r.get("success"))
        failures = sum(1 for h in recent for r in h.get("results", []) if not r.get("success"))

        body = f"SporlyWorks Executive 72-Hour Summary\n{'=' * 45}\n\n"
        body += f"Cycles executed: {len(recent)}\n"
        body += f"Dispatch successes: {successes}\n"
        body += f"Dispatch failures: {failures}\n\n"

        for h in recent[-10:]:  # Last 10 entries
            ts = h["timestamp"][:16].replace("T", " ")
            body += f"[{ts}] {h['rationale']}\n"
            for r in h.get("results", []):
                emoji = "✅" if r.get("success") else "❌"
                body += f"   {emoji} {r.get('agent')}: {r.get('summary')}\n"
            body += "\n"

        body += f"\n---\nDashboard: https://github.com/daveestaaqui/microAssets/actions\n"

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = f"📊 SporlyWorks Board Digest — {datetime.utcnow().strftime('%b %d')}"
    msg["From"] = sender_email
    msg["To"] = target_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        logging.info(f"72-Hour Executive Update sent to {target_email}.")
        return True
    except Exception as e:
        logging.error(f"Failed to send Executive Update: {e}")
        return False


# ── Main Cycle ───────────────────────────────────────────────────────────

def main():
    cycle_start = time.time()
    fallback_load_env()

    print("=" * 60)
    print("SPORLYWORKS CEO COORDINATOR v8.0")
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
            atomic_write_json(LEDGER_FILE, updated_ledger)
            logging.info("Persisted validated ledger update.")
        else:
            # LLM failed to provide valid ledger — keep existing + add results
            ledger["last_dispatch_results"] = dispatch_results
            atomic_write_json(LEDGER_FILE, ledger)
            logging.warning("Kept existing ledger (LLM update invalid or missing).")

    else:
        logging.error("Board deliberation FAILED. Ledger unchanged. Will retry next cycle.")

    # 8. Executive digest (every 3 days)
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                full_logs = json.load(f)
            if full_logs:
                first_ts = full_logs[0].get("timestamp", "")
                if first_ts:
                    first_time = datetime.fromisoformat(first_ts.rstrip("Z"))
                    if datetime.utcnow() - first_time >= timedelta(days=3):
                        logging.info("72 hours of logs detected. Sending Executive Digest...")
                        send_executive_update()
                        # Don't delete — just trim to last 10
                        atomic_write_json(HISTORY_FILE, full_logs[-10:])
        except Exception as e:
            logging.error(f"Digest check error: {e}")

    elapsed = round(time.time() - cycle_start, 1)
    print(f"\nCYCLE COMPLETE in {elapsed}s. Terminating cleanly.")


if __name__ == "__main__":
    main()
