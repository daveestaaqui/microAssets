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

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")

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

def get_latest_otp(max_retries=12, delay_seconds=5):
    """Connects to Gmail and fetches the latest 6-digit Instagram verification code with retries."""
    if not GMAIL_USER or not GMAIL_PASS:
        print("⚠️ GMAIL_USER or GMAIL_PASS not configured; cannot fetch OTP automatically.")
        return None

    print(f"⏳ Connecting to Gmail IMAP to search for Instagram verification code (up to {max_retries * delay_seconds}s)...")
    for attempt in range(1, max_retries + 1):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(GMAIL_USER, GMAIL_PASS)
            mail.select('"[Gmail]/All Mail"')
            
            # Search for recent emails mentioning Instagram
            status, messages = mail.search(None, '(FROM "instagram")')
            if status != "OK" or not messages[0]:
                status, messages = mail.search(None, 'ALL')

            if status == "OK" and messages[0]:
                ids = messages[0].split()
                if ids:
                    recent_ids = sorted(ids, key=lambda x: int(x), reverse=True)[:6]
                    for m_id in recent_ids:
                        res, msg_data = mail.fetch(m_id, "(RFC822)")
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                sender = str(msg.get("From", "")).lower()
                                subject = str(msg.get("Subject", "")).lower()
                                
                                if "instagram" in sender or "instagram" in subject or "security" in subject or "code" in subject:
                                    body = ""
                                    if msg.is_multipart():
                                        for part in msg.walk():
                                            if part.get_content_type() in ("text/html", "text/plain"):
                                                body += part.get_payload(decode=True).decode(errors='ignore')
                                    else:
                                        body = msg.get_payload(decode=True).decode(errors='ignore')
                                    
                                    codes = re.findall(r"\b\d{6}\b", body)
                                    if codes:
                                        print(f"✅ Found Instagram OTP on attempt {attempt}: {codes[0]} (Subject: {msg.get('Subject')})")
                                        mail.logout()
                                        return codes[0]
            mail.logout()
        except Exception as e:
            print(f"⚠️ Gmail IMAP attempt {attempt} notice: {e}")
        
        if attempt < max_retries:
            time.sleep(delay_seconds)

    print("❌ No Instagram OTP found in Gmail after maximum retries.")
    return None

def challenge_code_handler(username, choice):
    """Callback for instagrapi when a checkpoint security challenge occurs."""
    print(f"⚠️ Instagram login challenge ({choice}) triggered for @{username}. Waiting 10 seconds for email delivery...")
    time.sleep(10)
    return get_latest_otp(max_retries=12, delay_seconds=5)

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

def post_via_instagrapi(image_path, caption, username=None, password=None, session_id=None, delete_media_id=None):
    """Posts an image using the instagrapi client with session persistence and auto-OTP solving."""
    from instagrapi import Client

    # Tier 1: Try Session ID if provided
    if session_id:
        print("🚀 Attempting to connect via Instagram session ID...")
        try:
            cl = Client()
            cl.login_by_sessionid(session_id)
            print("✅ Session ID authentication successful.")
            print("Uploading photo...")
            media = cl.photo_upload(image_path, caption)
            print(f"🎉 Post published successfully via Session ID! Media ID: {media.pk}")

            if delete_media_id:
                try:
                    print(f"🗑️ Attempting to delete previous post media ID: {delete_media_id}...")
                    cl.media_delete(delete_media_id)
                    print(f"✅ Successfully deleted previous media ID {delete_media_id}!")
                    target_file = os.path.join(BASE_DIR, "_marketing", "delete_target.txt")
                    if os.path.exists(target_file):
                        os.remove(target_file)
                except Exception as de:
                    print(f"⚠️ Media deletion notice (can also delete directly in Instagram app): {de}")

            return True
        except Exception as se:
            print(f"⚠️ Session ID attempt failed: {se}")
            if not (username and password):
                return False
            print("🔄 Falling back to username/password login with automatic OTP resolver...")

    # Tier 2: Username and password login with automatic OTP challenge solver
    if username and password:
        print(f"🚀 Attempting login as @{username}...")
        try:
            cl = Client()
            cl.challenge_code_handler = challenge_code_handler
            try:
                cl.set_app("446.0.0.49.77")
            except Exception as ae:
                print(f"Notice setting app version: {ae}")

            cl.login(username, password)
            print("✅ Username/password login successful.")

            print("Uploading photo...")
            media = cl.photo_upload(image_path, caption)
            print(f"🎉 Post published successfully via credentials! Media ID: {media.pk}")

            if delete_media_id:
                try:
                    print(f"🗑️ Attempting to delete previous post media ID: {delete_media_id}...")
                    cl.media_delete(delete_media_id)
                    print(f"✅ Successfully deleted previous media ID {delete_media_id}!")
                    target_file = os.path.join(BASE_DIR, "_marketing", "delete_target.txt")
                    if os.path.exists(target_file):
                        os.remove(target_file)
                except Exception as de:
                    print(f"⚠️ Media deletion notice (can also delete directly in Instagram app): {de}")

            return True
        except Exception as ue:
            print(f"❌ Username/password login failed: {ue}")
            return False

    print("❌ Neither valid session ID nor username/password provided.")
    return False

def run_autoposter():
    parser = argparse.ArgumentParser(description="SporlyWorks Instagram Autoposter")
    parser.add_argument("--dry-run", action="store_true", help="Scan queue and drafts without posting")
    parser.add_argument("--session-id", help="Instagram sessionid cookie value (bypasses login challenges)")
    parser.add_argument("--username", help="Instagram username")
    parser.add_argument("--password", help="Instagram password")
    parser.add_argument("--access-token", help="Meta Graph API Page/User Access Token")
    parser.add_argument("--account-id", help="Meta Instagram Business Account ID")
    parser.add_argument("--delete-media-id", help="Delete a specific Instagram media ID")
    parser.add_argument("--update-avatar", action="store_true", help="Update Instagram profile picture using assets/instagram_avatar.jpg")
    args = parser.parse_args()

    state = load_state()

    # Standalone avatar update if requested
    if args.update_avatar:
        avatar_path = os.path.join(BASE_DIR, "assets", "instagram_avatar.jpg")
        print(f"🖼️ Attempting profile picture update from {avatar_path}...")
        try:
            from instagrapi import Client
            cl = Client()
            if args.session_id:
                cl.login_by_sessionid(args.session_id)
            elif args.username and args.password:
                cl.challenge_code_handler = challenge_code_handler
                cl.login(args.username, args.password)
            cl.account_change_picture(avatar_path)
            print("✅ Successfully updated Instagram profile picture!")
        except Exception as e:
            print(f"⚠️ Notice on profile picture update: {e}")
    
    # Standalone deletion if requested and queue is empty
    if args.delete_media_id and not os.path.exists(DRAFTS_DIR):
        print(f"🗑️ Deleting specified media ID: {args.delete_media_id}...")
        try:
            from instagrapi import Client
            cl = Client()
            if args.session_id:
                cl.login_by_sessionid(args.session_id)
            elif args.username and args.password:
                cl.login(args.username, args.password)
            cl.media_delete(args.delete_media_id)
            print(f"✅ Successfully deleted media ID {args.delete_media_id}!")
        except Exception as e:
            print(f"❌ Error deleting media: {e}")
        return

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
        if args.delete_media_id:
            print(f"🗑️ Deleting specified media ID: {args.delete_media_id}...")
            try:
                from instagrapi import Client
                cl = Client()
                if args.session_id:
                    cl.login_by_sessionid(args.session_id)
                elif args.username and args.password:
                    cl.login(args.username, args.password)
                cl.media_delete(args.delete_media_id)
                print(f"✅ Successfully deleted media ID {args.delete_media_id}!")
            except Exception as e:
                print(f"❌ Error deleting media: {e}")
            return
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

    # Try Unofficial Method (Session ID or Username/Password)
    elif args.session_id or (args.username and args.password):
        success = post_via_instagrapi(
            next_post["image"],
            caption,
            username=args.username,
            password=args.password,
            session_id=args.session_id,
            delete_media_id=args.delete_media_id
        )
        if success:
            state["published"].append(next_post["id"])
            save_state(state)
            return
    else:
        print("❌ Missing credentials. Specify either Meta Graph API args, session ID, or Instagram credentials.")

if __name__ == "__main__":
    run_autoposter()
