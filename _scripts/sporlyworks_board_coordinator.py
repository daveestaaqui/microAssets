#!/usr/bin/env python3
"""
SporlyWorks Autonomous Board Coordinator
========================================
A highly decoupled, platform-agnostic master orchestrator. 
This daemon manages the SporlyWorks "Undone Ledger" (the master roadmap of operational tasks) 
and dynamically instantiates and triggers 'Department Agents' (Marketing, DevOps, Security) 
via Webhooks / API calls to perform distributed work. 

It does not rely on local compute or bash commands.
Designed to run headless in Railway, Google Cloud Run, or GitHub Actions.
"""

import os
import json
import logging
import urllib.request
import urllib.parse
import smtplib
import time
import imaplib
import email
from email.header import decode_header
from email.message import EmailMessage
from datetime import datetime, timedelta
import sporlyworks_qa_agent

logging.basicConfig(
    format='%(asctime)s | Master Coordinator | [%(levelname)s] %(message)s',
    level=logging.INFO
)

# Use the script's own directory for all file paths (works locally and on CI)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Secrets Management (Ideally injected by Railway/Cloudflare)
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
RAILWAY_WEBHOOK_URL = os.environ.get("RAILWAY_WEBHOOK_URL", "https://api.railway.app/webhook/placeholder")

def fallback_load_env():
    """Fallback to load local .env if testing locally"""
    global OPENAI_KEY
    env_path = os.path.join(SCRIPT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k == "OPENAI_API_KEY": OPENAI_KEY = v

def fetch_recent_emails():
    """Connects to Gmail IMAP using SENDER_EMAIL and SENDER_APP_PASSWORD to fetch latest unread emails."""
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    if not sender_email or not sender_password:
        return "IMAP credentials missing. Cannot fetch correspondence."
        
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(sender_email, sender_password);
        mail.select("inbox")
        
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            return "No new unread correspondence."
            
        email_ids = messages[0].split()
        latest_ids = email_ids[-25:]
        
        inbound_str = ""
        for e_id in latest_ids:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")
                    inbound_str += f"- From: {from_} | Subject: {subject}\n"
        mail.logout()
        return inbound_str if inbound_str else "No new unread correspondence."
    except Exception as e:
        logging.error(f"IMAP Fetch Error: {e}")
        return f"Error fetching mail: {e}"

def ask_coordinator(ledger_state):
    """Secure isolated LLM caller triggering GPT-4o mapping"""
    if not OPENAI_KEY:
        logging.error("Missing OPENAI_KEY.")
        return None
        
    recent_emails = fetch_recent_emails()
        
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_KEY}"
    }
    
    prompt = f"""You are the Master Coordinator (CEO) of the SporlyWorks Executive Board.
You simulate a highly diverse Executive Board. As a collective, you operate with intense moral integrity, very high IQ, and exceptional EQ. You are experts in every field.
You govern a massive 87-extension SaaS portfolio.

CRITICAL DIRECTIVE: You must NEVER enter into legally binding agreements without authorization from David Mahler. Under no circumstances may you order an action that violates international law, CAN-SPAM, GDPR/CCPA, or constitutes trademark infringement.

Your primary directive is to analyze the 'Undone Ledger' and determine the highest-leverage action to execute right now.

CURRENT UNDONE LEDGER:
{json.dumps(ledger_state, indent=2)}

RECENT INBOUND CORRESPONDENCE:
{recent_emails}

Available Core Agents:
1. "MarketingAgent" (SEO, landing pages, B2B outreach)
2. "DevOpsAgent" (CWS packaging, API queuing)
3. "ComplianceAgent" (Chrome Web Store Privacy verifications)
4. "InfrastructureAgent" (Cloudflare DNS/Workers/KV, Railway deployments)
5. "QAAgent" (Automated testing, link checking, consistency auditing)

IMPORTANT: If QA_FINDINGS below shows any issues, your FIRST priority should be to dispatch the appropriate agent to fix them. Dead links, missing files, and inconsistencies are customer-facing and must be resolved before marketing or expansion work.

QA_FINDINGS (from automated pre-flight audit):
{json.dumps(ledger_state.get('qa_last_report', dict()).get('findings', []), indent=2)}

Return FORMAT MUST BE EXACT JSON:
{{
  "board_rationale": "Explanation of why this action drives the most value.",
  "updated_ledger": {{"status": "Your re-written ledger."}},
  "dispatches": [
    {{
      "target_agent": "MarketingAgent",
      "action_summary": "Generate high-conversion B2B SEO",
      "payload": {{"app_id": "word-counter", "task": "generate_blog_post", "angle": "b2b_productivity"}}
    }}
  ]
}}"""
    data = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": prompt}],
        "temperature": 0.4,
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            res = result['choices'][0]['message']['content'].strip()
            if res.startswith("```json"): res = res[7:]
            if res.endswith("```"): res = res[:-3]
            return json.loads(res)
    except Exception as e:
        logging.error(f"Coordinator API Error: {e}")
        return None

LEDGER_FILE = os.path.join(SCRIPT_DIR, "board_ledger.json")

def fetch_undone_ledger():
    """Loads the persistent board ledger from disk. If none exists, returns empty."""
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)
    return {}

import sporlyworks_sub_agents

def trigger_department_webhook(dispatch):
    """Core Execution Hookup."""
    logging.info(f"==> Waking up [{dispatch.get('target_agent')}] Agent")
    sporlyworks_sub_agents.route_payload(dispatch, OPENAI_KEY)

HISTORY_FILE = os.path.join(SCRIPT_DIR, "board_history.json")

def log_accomplishment(board_rationale, dispatches):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
            
    history.append({
        "timestamp": datetime.now().isoformat(),
        "rationale": board_rationale,
        "actions_taken": [d.get("action_summary") for d in dispatches]
    })
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def send_executive_update():
    """Compiles the last 3 days of accomplishments and emails the founder."""
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    target_email = "sandwichfitness@gmail.com"
    
    if not sender_email or not sender_password:
        logging.warning("Missing SENDER_EMAIL or SENDER_APP_PASSWORD. Skipping email update.")
        return False
        
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
            
    cutoff = datetime.now() - timedelta(days=3)
    recent_actions = [h for h in history if datetime.fromisoformat(h["timestamp"]) >= cutoff]
    
    if not recent_actions:
        body = "The Board has maintained normal operations for the last 72 hours."
    else:
        body = "Executive 72-Hour Summary:\n\n"
        for h in recent_actions:
            date_str = datetime.fromisoformat(h["timestamp"]).strftime('%Y-%m-%d %H:%M')
            body += f"[{date_str}] Strategic Move: {h['rationale']}\n"
            for a in h["actions_taken"]:
                body += f"   -> Executed: {a}\n"
            body += "\n"
            
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"SporlyWorks Executive Update - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = sender_email
    msg['To'] = target_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        logging.info(f"Successfully sent 72-Hour Executive Update to {target_email}.")
        return True
    except Exception as e:
        logging.error(f"Failed to send Executive Update email: {e}")
        return False

def main():
    fallback_load_env()
    print("=" * 60)
    print("SPORLYWORKS SERVERLESS DAEMON ONLINE")
    print("=" * 60)
    
    ledger = fetch_undone_ledger()
    logging.info("Fetched Master Undone Ledger from State.")
    
    # ── QA PRE-FLIGHT AUDIT (mandatory every cycle) ──
    logging.info("Running QA pre-flight audit...")
    qa_report = sporlyworks_qa_agent.run_full_audit()
    ledger['qa_last_report'] = qa_report
    logging.info(f"QA Status: {qa_report['status']} | Portfolio: {qa_report['portfolio']} | Findings: {len(qa_report['findings'])}")
    if qa_report['findings']:
        for f in qa_report['findings']:
            logging.warning(f"  QA: {f}")
    
    # Save ledger with QA results before CEO deliberation
    with open(LEDGER_FILE, "w") as lf:
        json.dump(ledger, lf, indent=2)
    
    decisions = ask_coordinator(ledger)
    if decisions:
        logging.info(f"[Board Rationale]: {decisions.get('board_rationale')}")
        dispatches = decisions.get('dispatches', [])
        
        for dispatch in dispatches:
            trigger_department_webhook(dispatch)
            
        log_accomplishment(decisions.get('board_rationale'), dispatches)
        
        updated_ledger = decisions.get('updated_ledger')
        if updated_ledger:
            with open(LEDGER_FILE, "w") as f:
                json.dump(updated_ledger, f, indent=2)
            logging.info("Successfully persisted updated ledger state back to file.")
    else:
        logging.error("Failed to generate board decisions. Will retry next cycle.")

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            full_logs = json.load(f)
            if len(full_logs) > 0:
                first_record_time = datetime.fromisoformat(full_logs[0]["timestamp"])
                if datetime.now() - first_record_time >= timedelta(days=3):
                    logging.info("72 hours of logs detected. Compiling Executive Update...")
                    if send_executive_update():
                        with open(HISTORY_FILE, "w") as fw:
                            json.dump([], fw, indent=2)
                        
    print("CYCLE COMPLETE. Serverless Action Terminating cleanly.")

if __name__ == "__main__":
    main()
