"""
Opera Add-ons Payload Generator
================================
Since Opera lacks a public developer API for automated code submission, this job:
  1. Identifies Chromium extensions not yet published to Opera.
  2. Assembles them into compliant Opera .zip bundles.
  3. Deposits them into _opera_builds/ to queue them for manual web upload.

Runs weekly (Fridays 4 AM EST) via scheduler.
"""
import os
import json
import zipfile
import logging
import asyncio
import datetime

logger = logging.getLogger(__name__)

WORKSPACE_DIR = os.environ.get("MICROASSETS_DIR", os.path.expanduser("~/Desktop/microAssets"))
OPERA_BUILDS_DIR = os.path.join(WORKSPACE_DIR, "_opera_builds")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LEDGER_PATH = os.path.join(DATA_DIR, "opera_publish_ledger.json")

# Throttle: max builds per cycle to avoid flooding the user
MAX_PER_CYCLE = 5


def _get_ledger() -> dict:
    """Load the Opera queued ledger."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"published": {}, "queue": [], "last_run": None}


def _save_ledger(ledger: dict):
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)


def discover_unpublished_extensions(ledger: dict) -> list:
    """Find Chrome extensions that haven't been queued for Opera."""
    if not os.path.isdir(WORKSPACE_DIR):
        return []

    published = set(ledger.get("published", {}).keys())
    queued = set(ledger.get("queue", []))

    unpublished = []
    for d in sorted(os.listdir(WORKSPACE_DIR)):
        if d.startswith("_") or d.startswith(".") or d.endswith("-firefox"):
            continue
        full_path = os.path.join(WORKSPACE_DIR, d)
        if not os.path.isdir(full_path):
            continue
        
        # Valid extension if it has a manifest
        if os.path.exists(os.path.join(full_path, "manifest.json")):
            if d not in published and d not in queued:
                unpublished.append(d)

    return unpublished


def generate_opera_zip(slug: str) -> bool:
    """Zip an extension directory into _opera_builds/[slug].zip"""
    ext_dir = os.path.join(WORKSPACE_DIR, slug)
    os.makedirs(OPERA_BUILDS_DIR, exist_ok=True)
    zip_path = os.path.join(OPERA_BUILDS_DIR, f"{slug}.zip")
    
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(ext_dir):
                # Exclude git or hidden files
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file.startswith('.'):
                        continue
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, ext_dir)
                    zip_file.write(file_path, arcname)
        return True
    except Exception as e:
        logger.error(f"Failed to zip {slug} for Opera: {e}")
        return False


async def run():
    """
    Main Opera Assembly job.
    Discovers unpublished extensions, queues them, and zips up to MAX_PER_CYCLE per week.
    """
    from services.notifications import send_notification

    logger.info("[OPERA] Waking up — checking for unqueued Opera Add-ons...")

    ledger = _get_ledger()

    # Discover new extensions and add to queue
    new_exts = discover_unpublished_extensions(ledger)
    if new_exts:
        ledger.setdefault("queue", []).extend(new_exts)
        logger.info(f"[OPERA] Discovered {len(new_exts)} new extensions: {new_exts[:5]}...")

    queue = ledger.get("queue", [])
    if not queue:
        logger.info("[OPERA] Queue empty — all extensions assembled.")
        ledger["last_run"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _save_ledger(ledger)
        return

    # Take up to MAX_PER_CYCLE from queue
    batch = queue[:MAX_PER_CYCLE]
    remaining = queue[MAX_PER_CYCLE:]

    results = {"assembled": 0, "failed": 0}

    for slug in batch:
        success = generate_opera_zip(slug)
        
        if success:
            results["assembled"] += 1
            ledger["published"][slug] = {
                "status": "QUEUED_FOR_MANUAL",
                "assembled_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            logger.info(f"  [ASSEMBLED] Opera Add-on → {slug}.zip")
        else:
            results["failed"] += 1

    ledger["queue"] = remaining
    ledger["last_run"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    _save_ledger(ledger)

    # Notify
    total_assembled = len(ledger.get("published", {}))
    await send_notification(
        "🔴 Opera Packager Report",
        f"**Batch**: {len(batch)} processed\n"
        f"**Assembled to .zip**: {results['assembled']} | **Failed**: {results['failed']}\n"
        f"**Remaining in queue**: {len(remaining)}\n"
        f"**Total queued for manually uploading to Opera**: {total_assembled}",
        color=0xFF1B2D if results["failed"] == 0 else 0xFEE75C,
        fields=[
            {"name": "Batch Size", "value": str(len(batch)), "inline": True},
            {"name": "Queue Left", "value": str(len(remaining)), "inline": True},
            {"name": "Total Assembled", "value": str(total_assembled), "inline": True},
        ]
    )

    logger.info(f"[OPERA] Done. {results['assembled']} .zip files created in _opera_builds/. {len(remaining)} left in queue.")
