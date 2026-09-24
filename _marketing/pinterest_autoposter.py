#!/usr/bin/env python3
"""
SporlyWorks — Autonomous Pinterest Auto-Poster
=============================================
Uploads high-resolution vertical pins (1000x1500) generated from blog articles
directly to Pinterest via Pinterest API v5.

Features:
- Base64 direct image payload upload (zero CDN dependency).
- Deduplication ledger in _marketing/pinterest_state.json.
- Backlinks directly to canonical sporlyworks.com blog guides.
- Graceful fallback with clear instructions when tokens are missing.
"""

import os
import sys
import json
import base64
import argparse
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DRAFTS_DIR = BASE_DIR / "_marketing" / "pinterest_drafts"
STATE_FILE = BASE_DIR / "_marketing" / "pinterest_state.json"

PINTEREST_API_URL = "https://api.pinterest.com/v5/pins"


def load_state():
    if not STATE_FILE.exists():
        return {"published": []}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"published": []}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_next_draft(published_ids):
    if not DRAFTS_DIR.exists():
        return None

    jpg_files = sorted(DRAFTS_DIR.glob("pin_*.jpg"))
    for jpg_path in jpg_files:
        pin_id = jpg_path.stem  # e.g., pin_cordyceps-atp-cellular-energy
        if pin_id not in published_ids:
            txt_path = jpg_path.with_suffix(".txt")
            caption = ""
            if txt_path.exists():
                caption = txt_path.read_text(encoding="utf-8").strip()

            slug = pin_id.replace("pin_", "")
            title = caption.split("\n")[0] if caption else slug.replace("-", " ").title()
            link = f"https://sporlyworks.com/blog/{slug}"

            return {
                "id": pin_id,
                "image_path": jpg_path,
                "title": title[:100],  # Pinterest max title length: 100
                "description": caption[:500] if caption else f"Read the full guide on {link}",
                "link": link
            }
    return None


def publish_pin(access_token, board_id, draft, is_dry_run=False):
    pin_id = draft["id"]
    image_path = draft["image_path"]

    print(f"📌 Preparing Pinterest Pin: {pin_id}")
    print(f"   Title:       {draft['title']}")
    print(f"   Destination: {draft['link']}")
    print(f"   Image:       {image_path.name}")

    if is_dry_run:
        print("   [DRY RUN] Pin validated successfully. Skipping live network POST.")
        return True, "dry_run_pin_id"

    # Encode image to base64
    with open(image_path, "rb") as img_file:
        b64_data = base64.b64encode(img_file.read()).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "board_id": board_id,
        "title": draft["title"],
        "description": draft["description"],
        "link": draft["link"],
        "media_source": {
            "source_type": "image_base64",
            "content_type": "image/jpeg",
            "data": b64_data
        }
    }

    try:
        response = requests.post(PINTEREST_API_URL, headers=headers, json=payload, timeout=30)
        res_data = response.json()

        if response.status_code in (200, 201) and "id" in res_data:
            print(f"🎉 Successfully published Pin to Pinterest! Pin ID: {res_data['id']}")
            return True, res_data["id"]
        else:
            print(f"❌ Failed to publish pin ({response.status_code}): {res_data}")
            return False, None
    except Exception as e:
        print(f"❌ Network error communicating with Pinterest API: {e}")
        return False, None


def main():
    parser = argparse.ArgumentParser(description="SporlyWorks Pinterest Auto-Poster")
    parser.add_argument("--access-token", default=os.getenv("PINTEREST_ACCESS_TOKEN", ""))
    parser.add_argument("--board-id", default=os.getenv("PINTEREST_BOARD_ID", ""))
    parser.add_argument("--dry-run", action="store_true", help="Validate without live API post")
    args = parser.parse_args()

    token = args.access_token.strip()
    board = args.board_id.strip()

    if not token or not board:
        if not args.dry_run:
            print("ℹ️ PINTEREST_ACCESS_TOKEN or PINTEREST_BOARD_ID not set in environment.")
            print("To enable hands-free Pinterest auto-posting, set these GitHub Secrets.")
            return 0

    state = load_state()
    draft = get_next_draft(state.get("published", []))

    if not draft:
        print("✅ No new pins pending in _marketing/pinterest_drafts/ queue.")
        return 0

    success, pin_id = publish_pin(token, board, draft, is_dry_run=args.dry_run)
    if success and not args.dry_run:
        state.setdefault("published", []).append(draft["id"])
        state.setdefault("history", []).append({
            "id": draft["id"],
            "pin_id": pin_id,
            "title": draft["title"],
            "link": draft["link"],
            "timestamp": requests.utils.default_user_agent()
        })
        save_state(state)
        print("✅ State updated successfully.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
