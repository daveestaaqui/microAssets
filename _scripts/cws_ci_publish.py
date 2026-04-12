#!/usr/bin/env python3
"""
CWS CI Publisher — Secure Chrome Web Store upload for GitHub Actions
====================================================================
Uses environment variables for credentials instead of hardcoded tokens.

Env vars required:
  CWS_CLIENT_ID
  CWS_CLIENT_SECRET
  CWS_REFRESH_TOKEN
  PUBLISH_EXTENSIONS  — comma-separated list or "all"
"""

import os
import sys
import json
import time
import zipfile
import requests
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────
BASE_DIR = os.environ.get("GITHUB_WORKSPACE", os.path.expanduser("~/Desktop/microAssets"))
CWS_IDS_FILE = os.path.join(BASE_DIR, "_scripts", "cws_item_ids.json")
BUILDS_DIR = os.path.join(BASE_DIR, "_builds")

CLIENT_ID = os.environ.get("CWS_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CWS_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("CWS_REFRESH_TOKEN", "")

RATE_LIMIT_DELAY = 5  # seconds between API calls

# Which extensions to publish
PUBLISH_LIST = os.environ.get("PUBLISH_EXTENSIONS", "all")

# ─── Validation ──────────────────────────────────────────────
if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("❌ Missing CWS credentials. Set CWS_CLIENT_ID, CWS_CLIENT_SECRET, CWS_REFRESH_TOKEN")
    sys.exit(1)

if not os.path.isfile(CWS_IDS_FILE):
    print(f"❌ CWS item IDs file not found: {CWS_IDS_FILE}")
    # Try alternate location
    alt = os.path.join(BASE_DIR, "cws_item_ids.json")
    if os.path.isfile(alt):
        CWS_IDS_FILE = alt
        print(f"  → Found at: {alt}")
    else:
        sys.exit(1)

# ─── Auth ────────────────────────────────────────────────────
def get_access_token():
    print("🔑 Requesting CWS access token...")
    res = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    data = res.json()
    if "access_token" not in data:
        print(f"❌ Token error: {data}")
        sys.exit(1)
    print("✅ Access token acquired")
    return data["access_token"]

# ─── Zip Builder ─────────────────────────────────────────────
EXCLUDE = {'.DS_Store', '__pycache__', '.git', 'node_modules', '.zip', 'store_materials'}

def build_zip(ext_name):
    src_dir = os.path.join(BASE_DIR, ext_name)
    if not os.path.isdir(src_dir):
        return None
    if not os.path.isfile(os.path.join(src_dir, "manifest.json")):
        return None

    os.makedirs(BUILDS_DIR, exist_ok=True)
    zip_path = os.path.join(BUILDS_DIR, f"{ext_name}.zip")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE]
            for file in files:
                if file.startswith('.') or file.endswith('.zip'):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, src_dir)
                zf.write(full_path, rel_path)

    return zip_path

# ─── CWS API ────────────────────────────────────────────────
def upload_extension(token, zip_path, extension_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "x-goog-api-version": "2"
    }
    url = f"https://www.googleapis.com/upload/chromewebstore/v1.1/items/{extension_id}"

    with open(zip_path, 'rb') as f:
        res = requests.put(url, headers=headers, data=f)

    data = res.json()
    if data.get("uploadState") == "SUCCESS":
        return True, "SUCCESS"
    else:
        errors = data.get("itemError", [])
        msgs = [e.get("error_detail", str(e)) for e in errors] if errors else [str(data)]
        return False, "; ".join(msgs)

def publish_extension(token, extension_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "x-goog-api-version": "2",
        "Content-Length": "0"
    }
    url = f"https://www.googleapis.com/chromewebstore/v1.1/items/{extension_id}/publish?publishTarget=default"
    res = requests.post(url, headers=headers)
    data = res.json()

    if "OK" in data.get("status", []):
        return True, "PUBLISHED"
    else:
        detail = data.get("statusDetail", [])
        return False, "; ".join(detail) if detail else str(data)

# ─── Main ────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("🚀 CWS CI PUBLISHER — Starting")
    print("=" * 60)

    with open(CWS_IDS_FILE) as f:
        all_ids = json.load(f)

    # Filter to requested extensions
    if PUBLISH_LIST == "all":
        cws_ids = all_ids
    else:
        requested = [x.strip() for x in PUBLISH_LIST.split(",") if x.strip()]
        cws_ids = {k: v for k, v in all_ids.items() if k in requested}
        missing = [r for r in requested if r not in all_ids]
        if missing:
            print(f"⚠️  No CWS IDs for: {', '.join(missing)}")

    print(f"📋 Publishing {len(cws_ids)} of {len(all_ids)} extensions")

    token = get_access_token()

    results = {"uploaded": [], "upload_failed": [], "published": [], "publish_failed": [], "skipped": []}
    total = len(cws_ids)

    for i, (ext_name, ext_id) in enumerate(cws_ids.items(), 1):
        print(f"\n{'─' * 50}")
        print(f"[{i}/{total}] {ext_name} ({ext_id})")

        zip_path = build_zip(ext_name)
        if not zip_path:
            print(f"  ⚠️ SKIPPED: No source dir")
            results["skipped"].append(ext_name)
            continue

        # Upload
        print(f"  📤 Uploading...")
        success, msg = upload_extension(token, zip_path, ext_id)
        if success:
            print(f"  ✅ Upload: {msg}")
            results["uploaded"].append(ext_name)
        else:
            print(f"  ❌ Upload: {msg}")
            results["upload_failed"].append({"name": ext_name, "error": msg})

        time.sleep(RATE_LIMIT_DELAY)

        # Publish
        print(f"  🚀 Publishing...")
        success, msg = publish_extension(token, ext_id)
        if success:
            print(f"  ✅ Published: {msg}")
            results["published"].append(ext_name)
        else:
            print(f"  ⚠️ Publish: {msg}")
            results["publish_failed"].append({"name": ext_name, "error": msg})

        time.sleep(RATE_LIMIT_DELAY)

    # Summary
    print(f"\n{'=' * 60}")
    print("📊 RESULTS")
    print(f"{'=' * 60}")
    print(f"  ✅ Uploaded:       {len(results['uploaded'])}/{total}")
    print(f"  ❌ Upload Failed:  {len(results['upload_failed'])}/{total}")
    print(f"  ✅ Published:      {len(results['published'])}/{total}")
    print(f"  ⚠️  Publish Failed: {len(results['publish_failed'])}/{total}")
    print(f"  ⏭️  Skipped:        {len(results['skipped'])}/{total}")

    # Write GitHub Actions summary
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a") as f:
            f.write("## 🚀 CWS Publish Results\n\n")
            f.write(f"| Metric | Count |\n|---|---|\n")
            f.write(f"| ✅ Uploaded | {len(results['uploaded'])}/{total} |\n")
            f.write(f"| ❌ Upload Failed | {len(results['upload_failed'])}/{total} |\n")
            f.write(f"| ✅ Published | {len(results['published'])}/{total} |\n")
            f.write(f"| ⚠️ Publish Failed | {len(results['publish_failed'])}/{total} |\n")
            f.write(f"| ⏭️ Skipped | {len(results['skipped'])}/{total} |\n\n")

            if results["publish_failed"]:
                f.write("### ⚠️ Publish Failures\n")
                for item in results["publish_failed"]:
                    f.write(f"- **{item['name']}**: {item['error']}\n")

    # Exit with error if anything critical failed
    if results["upload_failed"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
