#!/usr/bin/env python3
"""
CWS Wave Submission System
============================
Intelligent submission pipeline that respects CWS slot limits.

Architecture:
  1. This script submits the current wave
  2. The Cloudflare Email Worker detects approval emails and logs them to KV
  3. The Railway Worker's cws_monitor job detects approvals and auto-submits the next batch
  4. When all slots are used, the system requests a slot expansion via the CWS support form

Usage:
    python3 submit_for_review.py                  # Dry run — show current wave
    python3 submit_for_review.py --submit          # Submit current wave
    python3 submit_for_review.py --status          # Show queue status
    python3 submit_for_review.py --next-batch N    # Submit next N approved slots
"""
import json
import os
import sys
import time
import requests
from datetime import datetime

# === Config ===
BATCH_DELAY = 5        # seconds between individual submissions
MAX_RETRIES = 3
DRY_RUN = "--submit" not in sys.argv and "--next-batch" not in sys.argv

CWS_CLIENT_ID = os.environ.get("CWS_CLIENT_ID", "")
CWS_CLIENT_SECRET = os.environ.get("CWS_CLIENT_SECRET", "")
CWS_REFRESH_TOKEN = os.environ.get("CWS_REFRESH_TOKEN", "")

QUEUE_PATH = os.path.join(os.path.dirname(__file__), "cws_submission_queue.json")
CWS_IDS_PATH = os.path.join(os.path.dirname(__file__), "cws_item_ids.json")


def load_queue():
    with open(QUEUE_PATH) as f:
        return json.load(f)

def save_queue(queue):
    with open(QUEUE_PATH, 'w') as f:
        json.dump(queue, f, indent=2)

def load_cws_ids():
    with open(CWS_IDS_PATH) as f:
        return json.load(f)


def get_access_token():
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CWS_CLIENT_ID,
        "client_secret": CWS_CLIENT_SECRET,
        "refresh_token": CWS_REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    resp.raise_for_status()
    return resp.json()["access_token"]


def publish_item(item_id, token, slug):
    url = f"https://www.googleapis.com/chromewebstore/v1.1/items/{item_id}/publish"
    headers = {
        "Authorization": f"Bearer {token}",
        "x-goog-api-version": "2",
        "Content-Length": "0"
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(url, headers=headers)
            result = resp.json()
            status_detail = result.get("status", ["UNKNOWN"])[0]
            
            if resp.status_code == 200 and status_detail in ("OK", "PUBLISHED_WITH_FRICTION_WARNING"):
                return {"slug": slug, "status": "submitted", "detail": status_detail}
            elif status_detail == "ITEM_PENDING_REVIEW":
                return {"slug": slug, "status": "already_in_review", "detail": status_detail}
            elif status_detail == "ITEM_ALREADY_PUBLISHED":
                return {"slug": slug, "status": "already_published", "detail": status_detail}
            elif "ITEM_NOT_UPDATABLE" in str(result):
                return {"slug": slug, "status": "slot_limit", "detail": "Slot limit reached"}
            elif resp.status_code == 429:
                wait = 60 * (attempt + 1)
                print(f"  ⏳ Rate limited on {slug}, waiting {wait}s...")
                time.sleep(wait)
                continue
            else:
                return {"slug": slug, "status": "error", "detail": str(result)}
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(5 * (attempt + 1))
                continue
            return {"slug": slug, "status": "exception", "detail": str(e)}
    
    return {"slug": slug, "status": "max_retries", "detail": "Exhausted retries"}


def show_status():
    queue = load_queue()
    print(f"\n{'═'*55}")
    print(f"  CWS SUBMISSION QUEUE STATUS")
    print(f"  Max slots: {queue['config']['max_slots']}")
    print(f"{'═'*55}\n")
    
    total_submitted = len(queue.get("submissions", {}))
    total_approved = len(queue.get("approvals", {}))
    
    for wave_name, wave in queue["waves"].items():
        icon = {"pending": "🟡", "submitted": "🟢", "queued": "⚪", "partial": "🟠"}.get(wave["status"], "⚪")
        count = len(wave["items"])
        print(f"  {icon} {wave_name}: {wave['status'].upper()} ({count} items) — {wave['note']}")
    
    print(f"\n  📊 Submitted: {total_submitted} | Approved: {total_approved} | Slots available: {queue['config']['max_slots'] - total_submitted + total_approved}")
    print()


def submit_wave(wave_name=None, max_count=None):
    queue = load_queue()
    cws_ids = load_cws_ids()
    
    # Find the active wave
    if wave_name is None:
        for wn, wave in queue["waves"].items():
            if wave["status"] in ("pending", "partial"):
                wave_name = wn
                break
    
    if wave_name is None:
        print("No pending waves to submit.")
        return
    
    wave = queue["waves"][wave_name]
    items = wave["items"]
    
    if max_count:
        # Only submit up to max_count items that haven't been submitted yet
        items = [s for s in items if s not in queue.get("submissions", {})][:max_count]
    
    print(f"\n{'═'*55}")
    print(f"  SUBMITTING: {wave_name}")
    print(f"  Items: {len(items)}")
    print(f"  Mode: {'🔴 DRY RUN' if DRY_RUN else '🟢 LIVE'}")
    print(f"{'═'*55}\n")
    
    if DRY_RUN:
        for i, slug in enumerate(items, 1):
            cws_id = cws_ids.get(slug, "???")
            print(f"  [{i:2d}] {slug} → {cws_id}")
        print(f"\nTo submit: python3 submit_for_review.py --submit")
        return
    
    # Verify credentials
    if not all([CWS_CLIENT_ID, CWS_CLIENT_SECRET, CWS_REFRESH_TOKEN]):
        print("❌ Missing CWS API credentials.")
        sys.exit(1)
    
    print("🔐 Getting access token...")
    token = get_access_token()
    print("✅ Authenticated\n")
    
    results = {"submitted": 0, "already_in_review": 0, "already_published": 0, "slot_limit": 0, "error": 0}
    slot_limit_hit = False
    
    for i, slug in enumerate(items, 1):
        cws_id = cws_ids.get(slug)
        if not cws_id:
            print(f"  [{i:2d}] ⚠️  {slug} — no CWS ID found, skipping")
            continue
        
        print(f"  [{i:2d}/{len(items)}] {slug}...", end=" ", flush=True)
        result = publish_item(cws_id, token, slug)
        
        status = result["status"]
        results[status] = results.get(status, 0) + 1
        
        if status == "submitted":
            print(f"✅ Submitted")
            queue.setdefault("submissions", {})[slug] = {
                "cws_id": cws_id,
                "submitted_at": datetime.now().isoformat(),
                "wave": wave_name,
                "status": "pending_review"
            }
        elif status == "already_in_review":
            print(f"⏳ Already in review")
            queue.setdefault("submissions", {})[slug] = {
                "cws_id": cws_id,
                "submitted_at": datetime.now().isoformat(),
                "wave": wave_name,
                "status": "in_review"
            }
        elif status == "already_published":
            print(f"✅ Already published")
            queue.setdefault("approvals", {})[slug] = {
                "approved_at": datetime.now().isoformat()
            }
        elif status == "slot_limit":
            print(f"🚫 SLOT LIMIT REACHED — stopping")
            slot_limit_hit = True
            break
        else:
            print(f"❌ {result['detail']}")
        
        time.sleep(BATCH_DELAY)
    
    # Update wave status
    submitted_in_wave = [s for s in wave["items"] if s in queue.get("submissions", {}) or s in queue.get("approvals", {})]
    if len(submitted_in_wave) >= len(wave["items"]):
        wave["status"] = "submitted"
    elif len(submitted_in_wave) > 0:
        wave["status"] = "partial"
    
    save_queue(queue)
    
    # Summary
    print(f"\n{'═'*55}")
    print(f"  RESULTS")
    print(f"{'═'*55}")
    print(f"  ✅ Submitted: {results['submitted']}")
    print(f"  ⏳ Already in review: {results['already_in_review']}")
    print(f"  ✅ Already published: {results['already_published']}")
    print(f"  🚫 Slot limit: {results['slot_limit']}")
    print(f"  ❌ Errors: {results['error']}")
    
    if slot_limit_hit:
        print(f"\n  ⚠️  Slot limit reached. The auto-expansion system will:")
        print(f"     1. Monitor for approval emails via Cloudflare Email Worker")
        print(f"     2. Auto-submit the next batch when slots free up")
        print(f"     3. Request slot expansion when all {queue['config']['max_slots']} slots are used")


def submit_next_batch(count):
    """Called by the Railway worker when approvals free up slots."""
    queue = load_queue()
    
    for wave_name, wave in queue["waves"].items():
        if wave["status"] in ("queued", "partial"):
            unsubmitted = [s for s in wave["items"] if s not in queue.get("submissions", {}) and s not in queue.get("approvals", {})]
            if unsubmitted:
                print(f"Auto-submitting {min(count, len(unsubmitted))} items from {wave_name}")
                submit_wave(wave_name, max_count=count)
                return
    
    print("All waves submitted!")


def main():
    if "--status" in sys.argv:
        show_status()
    elif "--next-batch" in sys.argv:
        idx = sys.argv.index("--next-batch")
        count = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else 5
        submit_next_batch(count)
    else:
        submit_wave()


if __name__ == "__main__":
    main()
