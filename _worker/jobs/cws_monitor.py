"""
CWS Queue Monitor + Auto-Expansion System
==========================================
Two responsibilities:

1. MONITOR: Polls CWS API to detect when submitted extensions clear review
2. AUTO-EXPAND: When approvals are detected (via KV counter from email worker),
   automatically submits the next batch from the submission queue

Flow:
  - Cloudflare Email Worker detects Google "published" emails
  - Worker increments `cws_approval_count` in KV
  - This job reads the counter and compares against last-known count
  - If new approvals are detected, tries to submit next batch via CWS API
  - Sends Discord notification with status

Slot expansion:
  - When all 20 initial slots are used and extensions are approved,
  - the approved ones free up slots for new submissions
  - Google also auto-increases limits over time for healthy accounts
"""
import os
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

CWS_ITEM_IDS_JSON = os.environ.get("CWS_ITEM_IDS", "{}")
QUEUE_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "cws_submission_queue.json")

# In-memory state
_last_known_approval_count = 0
_last_auto_submit_time = None


def load_queue():
    """Load submission queue if available."""
    try:
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE) as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"[CWS] Failed to load queue: {e}")
    return None


def save_queue(queue):
    """Save submission queue."""
    try:
        with open(QUEUE_FILE, 'w') as f:
            json.dump(queue, f, indent=2)
    except Exception as e:
        logger.error(f"[CWS] Failed to save queue: {e}")


def get_next_wave(queue):
    """Find the next wave that has unsubmitted items."""
    submissions = queue.get("submissions", {})
    approvals = queue.get("approvals", {})
    
    for wave_name, wave in queue.get("waves", {}).items():
        if wave["status"] in ("queued", "partial"):
            unsubmitted = [
                s for s in wave["items"]
                if s not in submissions and s not in approvals
            ]
            if unsubmitted:
                return wave_name, unsubmitted
    return None, []


def count_pending_reviews(queue):
    """Count extensions submitted but not yet approved."""
    submissions = queue.get("submissions", {})
    approvals = queue.get("approvals", {})
    return sum(1 for slug in submissions if slug not in approvals and submissions[slug].get("status") != "rejected")


async def run():
    """
    Main CWS queue monitor + auto-expansion job.
    Called every 60 minutes by the scheduler.
    """
    global _last_known_approval_count, _last_auto_submit_time
    
    from services.notifications import send_notification, send_success, send_alert
    
    logger.info("[CWS] Running CWS monitor + auto-expansion check...")
    
    # Load the submission queue
    queue = load_queue()
    if not queue:
        logger.info("[CWS] No submission queue found — running in basic monitor mode")
        await run_basic_monitor()
        return
    
    # Load CWS IDs
    try:
        cws_ids_path = os.path.join(os.path.dirname(__file__), "..", "..", "cws_item_ids.json")
        with open(cws_ids_path) as f:
            cws_ids = json.load(f)
    except Exception:
        cws_ids = json.loads(CWS_ITEM_IDS_JSON) if CWS_ITEM_IDS_JSON else {}

    # Check status of submitted extensions
    submissions = queue.get("submissions", {})
    approvals = queue.get("approvals", {})
    max_slots = queue.get("config", {}).get("max_slots", 20)
    
    pending = count_pending_reviews(queue)
    available_slots = max_slots - pending
    
    logger.info(f"[CWS] Status: {len(submissions)} submitted, {len(approvals)} approved, {pending} pending, {available_slots} slots available")
    
    # Check for newly approved extensions via CWS API
    new_approvals = 0
    from services.cws_client import get_item_status
    
    for slug, sub_info in list(submissions.items()):
        if slug in approvals:
            continue  # Already known approved
        
        cws_id = sub_info.get("cws_id") or cws_ids.get(slug)
        if not cws_id:
            continue
        
        try:
            status = await get_item_status(cws_id)
            item_status = str(status.get("status", status.get("uploadState", "")))
            
            if "PUBLISHED" in item_status or "SUCCESS" in item_status:
                approvals[slug] = {
                    "approved_at": datetime.now().isoformat(),
                    "detected_by": "cws_monitor_api"
                }
                sub_info["status"] = "published"
                new_approvals += 1
                logger.info(f"  ✅ {slug} is now PUBLISHED")
            elif "REJECTED" in item_status:
                sub_info["status"] = "rejected"
                logger.warning(f"  🚫 {slug} was REJECTED")
        except Exception as e:
            logger.debug(f"  ⚠️ Could not check {slug}: {e}")
        
        # Don't hammer the API
        await asyncio.sleep(0.5)
    
    queue["approvals"] = approvals
    
    if new_approvals > 0:
        available_slots = max_slots - count_pending_reviews(queue)
        logger.info(f"[CWS] 🎉 {new_approvals} new approvals detected! {available_slots} slots now available")
        
        await send_success(
            f"🎉 **{new_approvals} CWS Extensions Approved!**\n\n"
            f"Slots available: **{available_slots}/{max_slots}**\n"
            f"Total approved: **{len(approvals)}**"
        )
    
    # Auto-submit next batch if slots are available
    if available_slots > 0:
        next_wave, unsubmitted = get_next_wave(queue)
        
        if next_wave and unsubmitted:
            batch_size = min(available_slots, len(unsubmitted), 5)  # Max 5 at a time
            batch = unsubmitted[:batch_size]
            
            logger.info(f"[CWS] 🚀 Auto-submitting {batch_size} items from {next_wave}: {batch}")
            
            # Get token and submit
            try:
                from services.cws_client import publish_item
                
                submitted = 0
                failed_items = []
                
                for slug in batch:
                    cws_id = cws_ids.get(slug)
                    if not cws_id:
                        logger.warning(f"  ⚠️ No CWS ID for {slug}")
                        continue
                    
                    try:
                        result = await publish_item(cws_id)
                        pub_status = str(result.get("status", []))
                        
                        if "OK" in pub_status or "PUBLISHED" in pub_status or "FRICTION" in pub_status:
                            submissions[slug] = {
                                "cws_id": cws_id,
                                "submitted_at": datetime.now().isoformat(),
                                "wave": next_wave,
                                "status": "pending_review"
                            }
                            submitted += 1
                            logger.info(f"  ✅ Auto-submitted: {slug}")
                        elif "ITEM_NOT_UPDATABLE" in pub_status or "limit" in pub_status.lower():
                            logger.warning(f"  🚫 Slot limit hit on {slug}")
                            break  # Stop trying
                        else:
                            failed_items.append(slug)
                            logger.warning(f"  ❌ {slug}: {result}")
                    except Exception as e:
                        failed_items.append(slug)
                        logger.error(f"  ❌ {slug}: {e}")
                    
                    await asyncio.sleep(2)
                
                queue["submissions"] = submissions
                
                # Update wave status
                wave = queue["waves"][next_wave]
                all_done = all(s in submissions or s in approvals for s in wave["items"])
                wave["status"] = "submitted" if all_done else "partial"
                
                if submitted > 0:
                    await send_notification(
                        "🚀 CWS Auto-Expansion",
                        f"**Wave**: {next_wave}\n"
                        f"**Submitted**: {submitted} new extensions\n"
                        f"**Failed**: {len(failed_items)}\n"
                        f"**Pending review**: {count_pending_reviews(queue)}/{max_slots}",
                        color=0x57F287
                    )
                
                _last_auto_submit_time = datetime.now().isoformat()
                
            except Exception as e:
                logger.error(f"[CWS] Auto-submit failed: {e}")
                await send_alert(f"CWS auto-expansion failed: {e}")
    else:
        next_wave, unsubmitted = get_next_wave(queue)
        if next_wave and unsubmitted:
            logger.info(f"[CWS] All {max_slots} slots in use. Waiting for approvals to free slots for {next_wave} ({len(unsubmitted)} items queued)")
    
    save_queue(queue)
    logger.info("[CWS] Monitor cycle complete")


async def run_basic_monitor():
    """Fallback: basic canary-based monitor when no queue file exists."""
    from services.notifications import send_alert
    from services.cws_client import get_item_status
    
    cws_ids = json.loads(CWS_ITEM_IDS_JSON) if CWS_ITEM_IDS_JSON else {}
    if not cws_ids:
        logger.warning("[CWS] No extension IDs configured")
        return
    
    canary_slug = os.environ.get("CWS_CANARY_SLUG", list(cws_ids.keys())[0])
    canary_id = cws_ids.get(canary_slug)
    
    if canary_id:
        try:
            status = await get_item_status(canary_id)
            logger.info(f"[CWS] Canary {canary_slug}: {status.get('status', 'unknown')}")
        except Exception as e:
            logger.error(f"[CWS] Canary check failed: {e}")
