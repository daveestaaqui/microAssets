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

logging.basicConfig(
    format='%(asctime)s | Master Coordinator | [%(levelname)s] %(message)s',
    level=logging.INFO
)

# Secrets Management (Ideally injected by Railway/Cloudflare)
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Used if triggering Github Action workflows
RAILWAY_WEBHOOK_URL = os.environ.get("RAILWAY_WEBHOOK_URL", "https://api.railway.app/webhook/placeholder")

def fallback_load_env():
    """Fallback to load local .env if testing locally"""
    global OPENAI_KEY
    env_path = os.path.join(os.path.expanduser("~/Desktop/microAssets/_scripts"), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k == "OPENAI_API_KEY": OPENAI_KEY = v

def fetch_recent_emails():
    """Connects to Gmail IMAP using SENDER_EMAIL and SENDER_APP_PASSWORD to fetch latest 5 unread emails."""
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
            return "No new unread correspondence."
            
        email_ids = messages[0].split()
        latest_ids = email_ids[-25:] # Fetch up to the last 25 unread emails for massive context
        
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
You simulate a highly diverse Executive Board (comprised of various genders, cultural backgrounds, and industries). As a collective, you operate with intense moral integrity, very high IQ, and exceptional Emotional Intelligence (EQ). You are experts in every field.
You govern a massive 87-extension SaaS portfolio. You aggressively monitor global macroeconomic, technological, and consumer trends to find new high-leverage opportunities before the market identifies them. You excel at identifying gaps in the market, driving exponential product growth, and expanding operations at an aggressive yet deeply calculated and appropriate rate. You make progress as quickly as reasonably possible.

CRITICAL DIRECTIVE: You have zero operational boundaries EXCEPT absolute legal safety. You must NEVER enter into legally binding agreements or contracts without a physical signature and authorization from David Mahler. If any negotiation requires a contract, explicitly generate an email task to contact sandwichfitness@gmail.com to request manual authorization. Under no circumstances may you order an action that violates international law, CAN-SPAM regulations, GDPR/CCPA privacy statutes, or constitutes trademark infringement. All growth tactics must be hyper-aggressive but 100% legally sound, honest, and ethical.

Your primary directive is to analyze the 'Undone Ledger' and determine the highest-leverage, most lucrative, or most strategically important operational move to execute right now. You do not write code—you assign work by dynamically dispatching tasks to dedicated Department Agents.

CURRENT UNDONE LEDGER:
{json.dumps(ledger_state, indent=2)}

RECENT INBOUND CORRESPONDENCE:
{recent_emails}

TASK: Read the ledger and recent correspondence. Leverage your collective diverse expertise to determine the absolute #1 highest-priority action required right now to safely drive SporlyWorks forward. 
Generate a strict JSON array dispatching that action to the proper dynamic agent. If a new type of agent is needed to fill a strategic gap, you may invent its target_agent name and define the task payload.

Available Core Agents (but you may invent new ones):
1. "MarketingAgent" (Handles SEO, landing pages, B2B outreach)
2. "DevOpsAgent" (Handles CWS packaging, API queuing)
3. "ComplianceAgent" (Handles Chrome Web Store Privacy Checklist verifications)
4. "InfrastructureAgent" (Handles modifying Cloudflare DNS, Cloudflare edge workers, KV state, and Railway deployments autonomously via REST API payloads)

Return FORMAT MUST BE EXACT JSON:
{{
  "board_rationale": "A highly intelligent, savvy explanation of why this specific action drives the most value and strategically positions the company right now.",
  "updated_ledger": {{"status": "Your completely re-written and modified ledger tracking current long term tasks. Cross off dispatched items and invent new ones as you steer the company."}},
  "dispatches": [
    {{
      "target_agent": "MarketingAgent",
      "action_summary": "Generate high-conversion B2B SEO targeting Enterprise HR",
      "payload": {{"app_id": "word-counter", "task": "generate_blog_post", "angle": "b2b_productivity"}}
    }}
  ]
}}"""

    data = json.dumps({
        "model": "gpt-4o-mini",  # Using max efficiency context layer
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

LEDGER_FILE = os.path.join(os.path.expanduser("~/Desktop/microAssets/_scripts"), "board_ledger.json")

def fetch_undone_ledger():
    """
    Loads the persistent board ledger from disk. If none exists, returns empty.
    """
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)
    return {}

import sporlyworks_sub_agents

def trigger_department_webhook(dispatch):
    """
    Core Execution Hookup. The Board Native Orchestrator calls the agents physically 
    rather than waiting for a separate webhook API setup, driving real-world files out.
    """
    logging.info(f"==> Waking up [{dispatch.get('target_agent')}] Agent")
    sporlyworks_sub_agents.route_payload(dispatch, OPENAI_KEY)

HISTORY_FILE = os.path.join(os.path.expanduser("~/Desktop/microAssets/_scripts"), "board_history.json")

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
        logging.warning("Missing SENDER_EMAIL or SENDER_APP_PASSWORD in .env. Skipping 72-hour email update.")
        return False
        
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
            
    # Filter only last 3 days
    cutoff = datetime.now() - timedelta(days=3)
    recent_actions = [h for h in history if datetime.fromisoformat(h["timestamp"]) >= cutoff]
    
    if not recent_actions:
        body = "The Board has maintained normal operations for the last 72 hours, but no new major tasks were generated."
    else:
        body = "Executive 72-Hour Summary:\\n\\n"
        for h in recent_actions:
            date_str = datetime.fromisoformat(h["timestamp"]).strftime('%Y-%m-%d %H:%M')
            body += f"[{date_str}] Strategic Move: {h['rationale']}\\n"
            for a in h["actions_taken"]:
                body += f"   -> Executed: {a}\\n"
            body += "\\n"
            
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
    print("="*60)
    print("🌐 SPORLYWORKS SERVERLESS DAEMON ONLINE")
    print("="*60)
    
    last_email_time = datetime.now()
    
    ledger = fetch_undone_ledger()
    logging.info("Fetched Master Undone Ledger from State.")
    
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
        logging.error("Failed to generate board decisions. Will retry next Serverless cycle.")

    # In a serverless GitHub action, we evaluate history directly rather than using process memory
    history_file_exists = os.path.exists(HISTORY_FILE)
    if history_file_exists:
        with open(HISTORY_FILE, "r") as f:
            full_logs = json.load(f)
            if len(full_logs) > 0:
                first_record_time = datetime.fromisoformat(full_logs[0]["timestamp"])
                if datetime.now() - first_record_time >= timedelta(days=3):
                    logging.info("72 hours of un-emailed logs detected. Compiling Executive Update for sandwichfitness...")
                    if send_executive_update():
                        # Clear logs after successful email
                        with open(HISTORY_FILE, "w") as fw:
                            json.dump([], fw, indent=2)
                        
    print("💤 CYCLE COMPLETE. Serverless Action Terminating cleanly.")

if __name__ == "__main__":
    main()
