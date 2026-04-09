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


# Use the script's own directory for all file paths (works locally and on CI)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Secrets Management (Ideally injected by Railway/Cloudflare)
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Used if triggering Github Action workflows
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
    """Connects to Gmail IMAP using SENDER_EMAIL and SENDER_APP_PASSWORD to fetch latest 5 unread emails."""
    s  sende_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    if not sender_email or not sender_password:
        return "IMAP credentials missing. Cannot fetch correspondence."
        
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(sender_email, sender_password)
