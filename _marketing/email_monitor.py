#!/usr/bin/env python3
import imaplib
import email
import re
import json
import os
import warnings
from pathlib import Path

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

BASE_DIR = Path("/Users/davidmahler/Desktop/microAssets")
CONFIG_PATH = BASE_DIR / "affiliate_config.json"

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Updated affiliate_config.json and saved successfully.")

def check_and_update_affiliates():
    print("=" * 60)
    print("  📧 SporlyWorks Automated Affiliate Email Monitor")
    print("=" * 60)
    
    # Login credentials from user's configured script
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login("sandwichfitness@gmail.com", "nxgfaiebqpmobhkp")
        mail.select("inbox")
    except Exception as e:
        print(f"❌ Failed to connect to Gmail: {e}")
        return

    config = load_config()
    updated = False

    # Define search terms and regex patterns for partners
    partner_rules = {
        "freshcap": {
            "search_sender": "impact.com",
            "keywords": ["freshcap", "impact.com", "approved", "partner", "application"],
            "regex": r"(?:ref=|subId=|partner/)([a-zA-Z0-9_\-]+)",
            "config_key": "freshcap"
        },
        "realmushrooms": {
            "search_sender": "realmushrooms.com",
            "keywords": ["real mushrooms", "affiliate", "approved", "ref="],
            "regex": r"(?:ref=|aff=)([a-zA-Z0-9_\-]+)",
            "config_key": "realmushrooms"
        },
        "seed": {
            "search_sender": "seed.com",
            "keywords": ["partner", "approved", "seeduniversity", "ref="],
            "regex": r"(?:ref=)([a-zA-Z0-9_\-]+)",
            "config_key": "seed"
        }
    }

    for key, rule in partner_rules.items():
        print(f"Scanning inbox for {rule['config_key']} updates...")
        
        # Check current config status
        current_id = config.get("partners", {}).get(key, {}).get("affiliate_id", "")
        if current_id and not current_id.startswith("YOUR_"):
            print(f"  ℹ️ {key} already has a valid ID: {current_id}. Skipping search.")
            continue

        # Search query matching sender or subject keywords
        status, messages = mail.search(None, f'ALL')
        if status != "OK" or not messages[0]:
            continue

        msg_ids = messages[0].split()
        # Scan last 50 emails
        for msg_id in reversed(msg_ids[-50:]):
            res, msg_data = mail.fetch(msg_id, "(RFC822)")
            for response_part in msg_data:
                if not isinstance(response_part, tuple):
                    continue
                
                msg = email.message_from_bytes(response_part[1])
                sender = str(msg.get('From', '')).lower()
                subject = str(msg.get('Subject', '')).lower()
                
                # Verify sender matches rule
                if rule["search_sender"] not in sender and not any(kw.lower() in subject for kw in rule["keywords"]):
                    continue
                
                # Fetch email body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors='ignore')

                # Run regex to find affiliate ID
                match = re.search(rule["regex"], body)
                if not match:
                    # check subject just in case
                    match = re.search(rule["regex"], subject)
                
                if match:
                    new_id = match.group(1)
                    print(f"  🎉 FOUND {key} Affiliate ID in email: {new_id}")
                    config["partners"][key]["affiliate_id"] = new_id
                    updated = True
                    break # stop scanning for this partner once found
            if updated:
                break

    if updated:
        save_config(config)
    else:
        print("No new affiliate IDs found in recent emails.")
    
    mail.logout()

if __name__ == "__main__":
    check_and_update_affiliates()
