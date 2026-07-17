import os
import sys
import re
import json
import time
import argparse
import imaplib
import email
import warnings
import requests

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Config and directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS_DIR = os.path.join(BASE_DIR, "_marketing", "instagram_drafts")
STATE_PATH = os.path.join(BASE_DIR, "_marketing", "instagram_state.json")

GMAIL_USER = "sandwichfitness@gmail.com"
GMAIL_PASS = "nxgfaiebqpmobhkp"

def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r") as f:
                return json.load(f)
        except:
            pass
    return {"published": []}

def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

def get_latest_otp():
    """Connects to Gmail and fetches the latest 6-digit Instagram verification code."""
    print("⏳ Connecting to Gmail IMAP to search for verification code...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASS)
        mail.select('"[Gmail]/All Mail"')
        
        # Search for recent emails from Instagram
        status, messages = mail.search(None, 'FROM "mail.instagram.com"')
        if status != "OK" or not messages[0]:
            mail.logout()
            return None
            
        ids = messages[0].split()
        # Fetch the latest email
        latest_id = sorted(ids, key=lambda x: int(x), reverse=True)[0]
        res, msg_data = mail.fetch(latest_id, "(RFC822)")
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/html" or part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode(errors='ignore')
                else:
                    body = msg.get_payload(decode=True).decode(errors='ignore')
                
                # Search for 6-digit numeric codes
                codes = re.findall(r"\b\d{6}\b", body)
                if codes:
                    print(f"✅ Found code in email: {codes[0]} (Email Subject: {msg.get('Subject')})")
                    mail.logout()
                    return codes[0]
        mail.logout()
    except Exception as e:
        print(f"❌ Error fetching OTP from Gmail: {e}")
    return None

def challenge_code_handler(username, choice):
    """Callback for instagrapi when a checkpoint security challenge occurs."""
    print(f"⚠️ Instagram login challenge triggered. Waiting 10 seconds for email...")
    time.sleep(10)
    return get_latest_otp()

def post_via_official_api(image_url, caption, access_token, instagram_account_id):
    """Posts an image using Meta's official Instagram Graph API."""
    print("🚀 Attempting to post via Official Meta Graph API...")
    try:
        # Step 1: Create media container
        container_url = f"https://graph.facebook.com/v19.0/{instagram_account_id}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": access_token
        }
        res = requests.post(container_url, data=payload)
        res_data = res.json()
        
        if "id" not in res_data:
            print(f"❌ Container creation failed: {res_data}")
            return False
            
        container_id = res_data["id"]
        print(f"✅ Container created: {container_id}. Publishing post...")
        
        # Step 2: Publish container
        publish_url = f"https://graph.facebook.com/v19.0/{instagram_account_id}/media_publish"
        publish_payload = {
            "creation_id": container_id,
            "access_token": access_token
        }
        pub_res = requests.post(publish_url, data=publish_payload)
        pub_data = pub_res.json()
        
        if "id" in pub_data:
            print(f"🎉 Post published successfully via Graph API! Post ID: {pub_data['id']}")
            return True
        else:
            print(f"❌ Publish failed: {pub_data}")
            return False
    except Exception as e:
        print(f"❌ Graph API exception: {e}")
        return False

def post_via_instagrapi(image_path, caption, username, password):
    """Posts an image using the unofficial instagrapi client with auto-OTP solving."""
    print("🚀 Attempting to post via Instagrapi client...")
    try:
        from instagrapi import Client
        cl = Client()
        
        # Inject our custom Gmail OTP solver callback
        cl.challenge_code_handler = challenge_code_handler
        
        print(f"Logging in as {username}...")
        cl.login(username, password)
        print("✅ Login successful.")
        
        # Post photo
        print("Uploading photo...")
        media = cl.photo_upload(image_path, caption)
        print(f"🎉 Post published successfully via Instagrapi! Media ID: {media.pk}")
        return True
    except Exception as e:
        print(f"❌ Instagrapi exception: {e}")
        return False

def run_autoposter():
    parser = argparse.ArgumentParser(description="SporlyWorks Instagram Autoposter")
    parser.add_argument("--dry-run", action="store_true", help="Scan queue and drafts without posting")
    parser.add_argument("--username", help="Instagram username")
    parser.add_argument("--password", help="Instagram password")
    parser.add_argument("--access-token", help="Meta Graph API Page/User Access Token")
    parser.add_argument("--account-id", help="Meta Instagram Business Account ID")
    parser.add_argument("--public-url", help="Publicly accessible URL of the image (needed for Graph API container)")
    args = parser.parse_args()

    state = load_state()
    
    # 1. Scan for drafts
    drafts = []
    if os.path.exists(DRAFTS_DIR):
        for file in sorted(os.listdir(DRAFTS_DIR)):
            if file.endswith(".jpg"):
                base = os.path.splitext(file)[0]
                cap_file = os.path.join(DRAFTS_DIR, f"{base}.txt")
                if os.path.exists(cap_file) and base not in state["published"]:
                    drafts.append({
                        "id": base,
                        "image": os.path.join(DRAFTS_DIR, file),
                        "caption_file": cap_file
                    })
                    
    if not drafts:
        print("✅ No new posts in the queue. All drafts published.")
        return

    next_post = drafts[0]
    print(f"📋 Found next post in queue: {next_post['id']}")
    
    with open(next_post["caption_file"], "r") as f:
        caption = f.read()

    print(f"\n--- CAPTION ---\n{caption}\n---------------")

    if args.dry_run:
        print("🔬 [DRY RUN] Would attempt to publish this post. Exiting.")
        return

    # Try Official Method
    if args.access_token and args.account_id and args.public_url:
        img_url = f"{args.public_url}/{next_post['id']}.jpg"
        success = post_via_official_api(img_url, caption, args.access_token, args.account_id)
        if success:
            state["published"].append(next_post["id"])
            save_state(state)
            return

    # Try Unofficial Method
    elif args.username and args.password:
        # Install instagrapi if not available
        try:
            import instagrapi
        except ImportError:
            print("⏳ Installing instagrapi library...")
            os.system(f"{sys.executable} -m pip install instagrapi")
            
        success = post_via_instagrapi(next_post["image"], caption, args.username, args.password)
        if success:
            state["published"].append(next_post["id"])
            save_state(state)
            return
    else:
        print("❌ Missing credentials. Specify either Meta Graph API args or Instagram credentials.")

if __name__ == "__main__":
    run_autoposter()
