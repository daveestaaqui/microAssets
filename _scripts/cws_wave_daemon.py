#!/usr/bin/env python3
"""
OmniSuite CWS Wave Daemon (Railway Worker)
==========================================
1. Listens for webhooks from the Cloudflare Email Worker (/webhook/cws-status).
2. Updates `cws_submission_queue.json` in response to published/rejected events.
3. Automatically commits and pushes the updated queue back to the GitHub `main` branch.
4. Auto-submits the next batch (Wave 2, Wave 3, etc.) when the pending queue drops below 18 items.
5. Runs via Flask + Gunicorn on Railway.
"""

import os
import sys
import json
import uuid
import time
import subprocess
from datetime import datetime
from threading import Thread
from flask import Flask, request, jsonify

app = Flask(__name__)

# ─── Configuration ───────────────────────────────────────────
AUTH_TOKEN = os.environ.get("OMNISUITE_SECRET", "super-secret-default")
BASE_DIR = os.environ.get("GITHUB_WORKSPACE", os.path.expanduser("~/Desktop/microAssets"))
QUEUE_FILE = os.path.join(BASE_DIR, "cws_submission_queue.json")
CWS_SCRIPT = os.path.join(BASE_DIR, "_scripts", "cws_ci_publish.py")

# The maximum items we want pending at any given time (Slot Limit)
MAX_PENDING_SLOTS = 18

def load_queue():
    if not os.path.isfile(QUEUE_FILE):
        return {"submissions": {}, "waves": {}}
    with open(QUEUE_FILE, "r") as f:
        return json.load(f)

def save_queue(data):
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def commit_and_push_state(event_msg="Update CWS submission queue state"):
    """
    Commits the cws_submission_queue.json back to GitHub to preserve state.
    Requires GITHUB_TOKEN environment variable in Railway.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token and not os.path.isdir(os.path.join(BASE_DIR, ".git")):
        print("⚠️ No GITHUB_TOKEN or .git dir found. Skipping remote push.")
        return False
        
    try:
        print(f"📦 Committing state: {event_msg}")
        # Configure git just in case this is a fresh container
        subprocess.run(["git", "config", "user.email", "omnisuite-bot@sporlyworks.com"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "config", "user.name", "OmniSuite Daemon"], cwd=BASE_DIR, check=False)
        
        subprocess.run(["git", "add", "cws_submission_queue.json"], cwd=BASE_DIR, check=True)
        # Avoid crash if no changes
        status = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
        if "cws_submission_queue.json" not in status.stdout:
            print("  → No changes to commit.")
            return True

        subprocess.run(["git", "commit", "-m", f"🤖 Auto-Sync: {event_msg}"], cwd=BASE_DIR, check=True)
        
        # Only push using token if we are on a Railway container
        if token:
            remote_url = f"https://x-access-token:{token}@github.com/daveestaaqui/microAssets.git"
            subprocess.run(["git", "push", remote_url, "main"], cwd=BASE_DIR, check=True)
        else:
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
            
        print("✅ State successfully pushed to GitHub.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False

def trigger_next_wave_if_needed():
    """
    Calculates how many pending items exist. If below MAX_PENDING_SLOTS,
    it identifies the next batch of unsubmitted extensions and fires cws_ci_publish.py.
    Runs asynchronously so the webhook response doesn't hang.
    """
    queue = load_queue()
    submissions = queue.get("submissions", {})
    
    # Calculate currently pending
    pending_count = sum(1 for ext, data in submissions.items() if data.get("status") == "pending_review")
    available_slots = MAX_PENDING_SLOTS - pending_count
    
    print(f"📊 Slot check: {pending_count} pending. {available_slots} slots available.")
    
    if available_slots <= 0:
        print("  → Queue is full. Waiting for more approvals.")
        return

    # Find the next wave extensions that haven't been submitted yet
    all_waves = queue.get("waves", {})
    next_batch = []
    
    # Sort waves to process sequentially (wave_1, wave_2, etc.)
    for wave_id in sorted(all_waves.keys()):
        wave_data = all_waves[wave_id]
        if wave_data.get("status") == "completed":
            continue
            
        extensions = wave_data.get("items", [])
        for ext in extensions:
            if ext not in submissions:
                next_batch.append(ext)
                if len(next_batch) >= available_slots:
                    break
        
        if len(next_batch) >= available_slots:
            break

    if not next_batch:
        print("🎉 Awesome news! No more extensions to publish. All waves complete.")
        return
        
    print(f"🚀 Triggering background submission for {len(next_batch)} extensions: {', '.join(next_batch)}")
    
    # Actually run the submission!
    def run_sub():
        env = os.environ.copy()
        env["PUBLISH_EXTENSIONS"] = ",".join(next_batch)
        print("  → Spawning cws_ci_publish.py...")
        result = subprocess.run([sys.executable, CWS_SCRIPT], env=env, cwd=BASE_DIR, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ Background publish succeeded:\n{result.stdout[-500:]}")
            # The script logic needs to update the queue. 
            # Because cws_submit_wave1.py did this but cws_ci_publish.py natively does NOT,
            # we must update the queue here based on successful execution.
            current_queue = load_queue()
            cws_ids = load_cws_ids()
            
            for ext in next_batch:
                current_queue.setdefault("submissions", {})[ext] = {
                    "cws_id": cws_ids.get(ext),
                    "submitted_at": datetime.now().isoformat(),
                    "wave": "auto_wave",
                    "status": "pending_review"
                }
            save_queue(current_queue)
            commit_and_push_state(f"Auto-submitted {len(next_batch)} items")
            
        else:
            print(f"  ❌ Background publish failed:\n{result.stderr[-500:]}")
            
    Thread(target=run_sub).start()

def load_cws_ids():
    ids_file = os.path.join(BASE_DIR, "cws_item_ids.json")
    if not os.path.isfile(ids_file):
        ids_file = os.path.join(BASE_DIR, "_scripts", "cws_item_ids.json")
    with open(ids_file, "r") as f:
        return json.load(f)

# ─── Flask Routes ───────────────────────────────────────────

@app.route("/webhook/cws-status", methods=["POST"])
def cws_status_webhook():
    """
    Endpoint for the Cloudflare Email Worker.
    Payload: { "timestamp": "...", "extension_name": "...", "event": "published"|"rejected" }
    """
    token = request.headers.get("X-Omnisuite-Token")
    if token != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    if not data:
        return jsonify({"error": "Bad Request"}), 400
        
    ext_name = data.get("extension_name", "UNKNOWN")
    event = data.get("event", "UNKNOWN")
    
    print(f"🔔 Received Webhook: [{event.upper()}] {ext_name}")
    
    queue = load_queue()
    submissions = queue.setdefault("submissions", {})
    
    # We must try to map the incoming extension name to our dir name
    # e.g. "JSON Formatter Pro" -> "json-formatter"
    # Actually, cws_submission_queue.json might track by directory key.
    # Let's find the matching extension entry where the name roughly matches,
    # or rely on direct mapping if known.
    
    # Since CWS names are full human-readable and directory names are sluggified,
    # this is a simple heuristic: replace spaces with hyphens, lowercase.
    target_key = None
    for k in submissions.keys():
        if k.replace("-", " ") in ext_name.lower():
            target_key = k
            break
            
    # Fallback to direct text search from the ids mapping
    if not target_key:
        cws_ids = load_cws_ids()
        # You might have a reverse lookup here, but let's assume we can fuzzy match
        for k in cws_ids.keys():
            if k.replace("-", " ") in ext_name.lower():
                target_key = k
                break
                
    if not target_key:
        print(f"⚠️ Could not map '{ext_name}' to an internal directory key. Adding as raw.")
        target_key = ext_name.lower().replace(" ", "-")
        
    # Update state
    submissions.setdefault(target_key, {})["status"] = event
    submissions[target_key]["updated_at"] = data.get("timestamp", datetime.now().isoformat())
    
    save_queue(queue)
    print(f"  📝 Saved state: {target_key} -> {event}")
    
    # Commit immediately
    commit_and_push_state(f"Update state for {target_key} ({event})")
    
    # If the item was published or rejected, a slot just freed up!
    if event in ["published", "rejected"]:
        # Fire the next wave check asynchronously
        Thread(target=trigger_next_wave_if_needed).start()

    return jsonify({"status": "success", "mapped_key": target_key}), 200

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "omnisuite-cws-daemon"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting OmniSuite CWS Daemon on port {port}")
    app.run(host="0.0.0.0", port=port)
