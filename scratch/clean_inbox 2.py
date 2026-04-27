import os
import requests
import logging

def purge_all():
    inbox_url = os.environ.get("CEO_INBOX_URL")
    inbox_secret = os.environ.get("CEO_INBOX_SECRET")
    
    if not inbox_url or not inbox_secret:
        print("Missing CEO_INBOX_URL or CEO_INBOX_SECRET. Check environment.")
        return

    # 1. Fetch ALL emails (assuming current API allows fetching all or we just fetch unread and delete)
    try:
        resp = requests.get(
            f"{inbox_url.rstrip('/')}/list",
            headers={"X-Inbox-Secret": inbox_secret},
            timeout=10
        )
        if resp.status_code != 200:
            print(f"Failed to fetch inbox: {resp.status_code}")
            return
            
        emails = resp.json().get("emails", [])
        if not emails:
            print("Inbox is already empty.")
            return
            
        ids = [e.get("id") for e in emails]
        print(f"Found {len(ids)} emails. Purging...")
        
        # 2. Delete them
        del_resp = requests.post(
            f"{inbox_url.rstrip('/')}/delete",
            headers={"X-Inbox-Secret": inbox_secret, "Content-Type": "application/json"},
            json={"ids": ids},
            timeout=10
        )
        if del_resp.status_code in (200, 204):
            print(f"Successfully purged {len(ids)} emails.")
        else:
            print(f"Delete failed: {del_resp.status_code} - {del_resp.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    purge_all()
