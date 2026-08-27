"""
Website Auto-Sync
=================
Keeps the GitHub Pages landing page in sync with the actual portfolio.
When extensions are added, updated, or Android apps published, this job:
  1. Updates the tool count on the homepage
  2. Appends to changelog.html
  3. Pushes changes to GitHub via API (no git clone needed)

Runs daily at 6 AM EST via scheduler.

Requires:
  GITHUB_TOKEN — Personal access token with repo scope
"""
import os
import re
import json
import base64
import logging
import datetime

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SYNC_STATE_PATH = os.path.join(DATA_DIR, "website_sync_state.json")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_LANDING_REPO", "daveestaaqui/micro-assets-landing-page")
GITHUB_API = "https://api.github.com"

WORKSPACE_DIR = os.environ.get("MICROASSETS_DIR", os.path.expanduser("~/Desktop/microAssets"))


def _get_sync_state() -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(SYNC_STATE_PATH):
        try:
            with open(SYNC_STATE_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_ext_count": 0, "last_android_count": 0, "last_sync": None, "changelog_entries": []}


def _save_sync_state(state: dict):
    with open(SYNC_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def count_extensions() -> dict:
    """Count Chrome, Firefox, and Android assets."""
    chrome = 0
    firefox = 0
    android = 0

    if os.path.isdir(WORKSPACE_DIR):
        for d in os.listdir(WORKSPACE_DIR):
            full = os.path.join(WORKSPACE_DIR, d)
            if not os.path.isdir(full) or d.startswith("_") or d.startswith("."):
                continue
            if d.endswith("-firefox"):
                firefox += 1
            else:
                chrome += 1

    aabs_dir = os.path.join(WORKSPACE_DIR, "_android_aabs")
    if os.path.isdir(aabs_dir):
        android = len([f for f in os.listdir(aabs_dir) if f.endswith(".aab")])

    return {"chrome": chrome, "firefox": firefox, "android": android, "total": chrome + firefox + android}


def detect_changes(state: dict, counts: dict) -> list:
    """Detect what changed since last sync."""
    changes = []

    new_chrome = counts["chrome"] - state.get("last_chrome_count", state.get("last_ext_count", 0))
    new_android = counts["android"] - state.get("last_android_count", 0)
    new_firefox = counts["firefox"] - state.get("last_firefox_count", 0)

    if new_chrome > 0:
        changes.append(f"+{new_chrome} new Chrome extension{'s' if new_chrome > 1 else ''}")
    if new_firefox > 0:
        changes.append(f"+{new_firefox} new Firefox extension{'s' if new_firefox > 1 else ''}")
    if new_android > 0:
        changes.append(f"+{new_android} new Android app{'s' if new_android > 1 else ''}")

    # Check play publisher ledger for recent publishes
    last_sync = state.get("last_sync", "2000-01-01")
    play_ledger_path = os.path.join(DATA_DIR, "play_publish_ledger.json")
    if os.path.exists(play_ledger_path):
        try:
            with open(play_ledger_path) as f:
                play = json.load(f)
            recent = [
                s for s, info in play.get("published", {}).items()
                if info.get("published_at", info.get("queued_at", "")) > last_sync
            ]
            if recent:
                changes.append(f"{len(recent)} Android app{'s' if len(recent) > 1 else ''} submitted to Play Store")
        except Exception:
            pass

    # Check Edge publisher ledger
    edge_ledger_path = os.path.join(DATA_DIR, "edge_publish_ledger.json")
    if os.path.exists(edge_ledger_path):
        try:
            with open(edge_ledger_path) as f:
                edge = json.load(f)
            recent = [
                s for s, info in edge.get("published", {}).items()
                if info.get("published_at", info.get("queued_at", "")) > last_sync
            ]
            if recent:
                changes.append(f"{len(recent)} extension{'s' if len(recent) > 1 else ''} deployed to Microsoft Edge Add-ons")
        except Exception:
            pass

    # Check Opera publisher ledger
    opera_ledger_path = os.path.join(DATA_DIR, "opera_publish_ledger.json")
    if os.path.exists(opera_ledger_path):
        try:
            with open(opera_ledger_path) as f:
                opera = json.load(f)
            recent = [
                s for s, info in opera.get("published", {}).items()
                if info.get("assembled_at", "") > last_sync
            ]
            if recent:
                changes.append(f"{len(recent)} extension{'s' if len(recent) > 1 else ''} assembled for Opera Store")
        except Exception:
            pass

    # Record software patches and new custom apps from the ledger
    audit_log_path = os.path.join(DATA_DIR, "audit_log.jsonl")
    if os.path.exists(audit_log_path):
        try:
            with open(audit_log_path, "r") as f:
                for line in f:
                    if not line.strip(): continue
                    event = json.loads(line)
                    if event.get("timestamp", "") > last_sync:
                        if event.get("event") == "SOFTWARE_FIXED":
                            d = event.get("details", {})
                            changes.append(f"Fixed an issue in **{d.get('slug', 'app')}**: {d.get('issue_resolved', 'Performance improvements')}")
                        elif event.get("event") == "APP_CREATED":
                            d = event.get("details", {})
                            changes.append(f"Launched new micro-app: **{d.get('name', 'Pro Tool')}** ({', '.join(d.get('platforms', ['web']))})")
        except Exception as e:
            logger.error(f"Failed to read audit log for sync: {e}")

    return changes


def generate_updated_index(counts: dict) -> str:
    """Generate updated hero badge and trust bar numbers for index.html."""
    total = counts["chrome"]  # Main count shown is Chrome extensions
    return str(total)


async def push_file_to_github(path: str, content: str, message: str, sha: str = None):
    """Push a file to GitHub via the Contents API."""
    import httpx

    if not GITHUB_TOKEN:
        logger.warning(f"[SYNC] No GITHUB_TOKEN — would push {path}: {message}")
        return False

    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Get current file SHA if not provided
    if sha is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                sha = resp.json().get("sha")

    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha

    async with httpx.AsyncClient() as client:
        resp = await client.put(url, headers=headers, json=payload, timeout=15.0)
        if resp.status_code in (200, 201):
            logger.info(f"[SYNC] Pushed {path} to GitHub")
            return True
        else:
            logger.error(f"[SYNC] Failed to push {path}: {resp.status_code} {resp.text[:200]}")
            return False


async def update_index_counts(counts: dict):
    """Update the hero badge and trust bar in index.html with current counts."""
    import httpx

    if not GITHUB_TOKEN:
        logger.info(f"[SYNC] Would update index.html: {counts['chrome']}+ extensions")
        return

    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/index.html"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=10.0)
        if resp.status_code != 200:
            logger.error(f"[SYNC] Could not fetch index.html: {resp.status_code}")
            return
        file_data = resp.json()
        sha = file_data["sha"]
        content = base64.b64decode(file_data["content"]).decode("utf-8")

    # Update the badge count
    chrome_count = counts["chrome"]
    updated = re.sub(
        r'(\d+)\+?\s*extensions\s*·\s*Trusted',
        f'{chrome_count}+ extensions · Trusted',
        content
    )

    # Update the trust bar count
    updated = re.sub(
        r'<strong>\d+\+?</strong>\s*extensions',
        f'<strong>{chrome_count}+</strong> extensions',
        updated
    )

    # Update the trust bar platform list specifically
    updated = re.sub(
        r'<strong>Chrome · Firefox · Android</strong>',
        '<strong>Chrome · Firefox · Android · Edge · Opera</strong>',
        updated
    )

    if updated != content:
        await push_file_to_github("index.html", updated, f"Auto-sync: {chrome_count}+ extensions", sha)
    else:
        logger.info("[SYNC] index.html already up to date")


async def append_changelog(changes: list):
    """Add a new changelog entry to changelog.html."""
    import httpx

    if not changes or not GITHUB_TOKEN:
        return

    today = datetime.date.today().isoformat()
    entry_html = f'<div class="entry"><h3>{today}</h3><ul>'
    for c in changes:
        entry_html += f'<li>{c}</li>'
    entry_html += '</ul></div>\n'

    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/changelog.html"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=10.0)

    if resp.status_code == 200:
        file_data = resp.json()
        sha = file_data["sha"]
        content = base64.b64decode(file_data["content"]).decode("utf-8")

        # Insert after the opening body/main tag
        insert_marker = "<!-- CHANGELOG_ENTRIES -->"
        if insert_marker in content:
            content = content.replace(insert_marker, insert_marker + "\n" + entry_html)
        else:
            # Append before </body>
            content = content.replace("</body>", entry_html + "\n</body>")

        await push_file_to_github("changelog.html", content, f"Changelog: {today} — {len(changes)} updates", sha)
    else:
        logger.info("[SYNC] changelog.html not found — skipping")


async def run():
    """
    Main website sync job.
    Detects portfolio changes and pushes updates to GitHub Pages.
    """
    from services.notifications import send_info

    logger.info("[SYNC] Checking for portfolio changes to sync to website...")

    state = _get_sync_state()
    counts = count_extensions()

    logger.info(f"[SYNC] Portfolio: {counts['chrome']} Chrome, {counts['firefox']} Firefox, {counts['android']} Android")

    changes = detect_changes(state, counts)

    if not changes:
        logger.info("[SYNC] No changes detected — website is current.")
        state["last_sync"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _save_sync_state(state)
        return

    logger.info(f"[SYNC] Detected {len(changes)} changes: {changes}")

    # 1. Update extension count on homepage
    await update_index_counts(counts)

    # 2. Append to changelog
    await append_changelog(changes)

    # 3. Update sync state
    state["last_chrome_count"] = counts["chrome"]
    state["last_firefox_count"] = counts["firefox"]
    state["last_android_count"] = counts["android"]
    state["last_sync"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    state["changelog_entries"].append({
        "date": datetime.date.today().isoformat(),
        "changes": changes,
    })
    _save_sync_state(state)

    # 4. Notify
    await send_info(
        f"🌐 **Website Auto-Synced**\n\n"
        + "\n".join([f"• {c}" for c in changes])
        + f"\n\n**Portfolio**: {counts['chrome']} Chrome · {counts['firefox']} Firefox · {counts['android']} Android"
    )

    logger.info("[SYNC] Website sync complete.")
