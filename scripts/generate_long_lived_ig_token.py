#!/usr/bin/env python3
"""
SporlyWorks — Meta Graph API Long-Lived Token Generator & IG Account ID Finder
Exchanges a short-lived Meta user access token for a 60-day Long-Lived Access Token
and automatically resolves your INSTAGRAM_ACCOUNT_ID for automated daily posting.
"""

import sys
import json
import urllib.request
import urllib.parse

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SporlyWorks-IG-Setup/1.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='ignore')
        print(f"❌ API Request Failed ({e.code}): {err_msg}")
        return None
    except Exception as e:
        print(f"❌ Network Error: {e}")
        return None

def exchange_and_get_details(app_id, app_secret, short_lived_token):
    print("\n🔄 1. Exchanging for Long-Lived User Access Token (60-day validity)...")
    
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id.strip(),
        "client_secret": app_secret.strip(),
        "fb_exchange_token": short_lived_token.strip()
    }
    url = f"https://graph.facebook.com/v19.0/oauth/access_token?{urllib.parse.urlencode(params)}"
    data = fetch_json(url)
    
    if not data or "access_token" not in data:
        print("❌ Could not generate long-lived token. Please check App ID, App Secret, and Token.")
        return
        
    long_lived_token = data["access_token"]
    expires_in = data.get("expires_in", "unknown")
    print(f"✅ Generated Long-Lived Token! (Expires in ~{int(expires_in)//86400 if str(expires_in).isdigit() else expires_in} days)")
    
    print("\n🔍 2. Locating Connected Instagram Business Account ID...")
    me_url = f"https://graph.facebook.com/v19.0/me/accounts?fields=name,id,instagram_business_account&access_token={long_lived_token}"
    me_data = fetch_json(me_url)
    
    ig_account_id = None
    if me_data and "data" in me_data:
        for page in me_data["data"]:
            if "instagram_business_account" in page:
                ig_account_id = page["instagram_business_account"]["id"]
                page_name = page.get("name", "Facebook Page")
                print(f"✅ Found Connected Page: {page_name}")
                print(f"✅ Found Instagram Business Account ID: {ig_account_id}")
                break
                
    print("\n" + "=" * 65)
    print("  🎉 YOUR GITHUB SECRETS ARE READY TO COPY-PASTE")
    print("=" * 65)
    print(f"\n1. INSTAGRAM_ACCESS_TOKEN:\n{long_lived_token}\n")
    if ig_account_id:
        print(f"2. INSTAGRAM_ACCOUNT_ID:\n{ig_account_id}\n")
    else:
        print("2. INSTAGRAM_ACCOUNT_ID:\n(Not automatically detected. Please ensure your Instagram is connected to a Facebook Page in Meta Business Suite.)")
        
    print("=" * 65)
    print("👉 Add these two secrets to GitHub: Settings -> Secrets and variables -> Actions")
    print("=" * 65)

def main():
    print("=" * 65)
    print(" 📸 SporlyWorks Meta Graph API Token Exchange Wizard")
    print("=" * 65)
    
    if len(sys.argv) == 4:
        app_id = sys.argv[1]
        app_secret = sys.argv[2]
        token = sys.argv[3]
    else:
        app_id = input("\nEnter Meta App ID: ").strip()
        app_secret = input("Enter Meta App Secret: ").strip()
        token = input("Enter Short-Lived Access Token (from Graph API Explorer): ").strip()
        
    if not app_id or not app_secret or not token:
        print("❌ Missing required fields. Exiting.")
        sys.exit(1)
        
    exchange_and_get_details(app_id, app_secret, token)

if __name__ == "__main__":
    main()
