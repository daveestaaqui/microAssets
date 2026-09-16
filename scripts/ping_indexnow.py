#!/usr/bin/env python3
"""
SporlyWorks — IndexNow Instant Search Engine Indexing Dispatcher
Submits newly generated URLs to IndexNow API (Bing, Yandex, Seznam, Naver)
using the verified key in sporlyworks-indexnow-key.txt.
"""
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
KEY_FILE = ROOT / "sporlyworks-indexnow-key.txt"
SITEMAP_FILE = ROOT / "sitemap.xml"
HOST = "sporlyworks.com"
INDEXNOW_API = "https://api.indexnow.org/indexnow"
BING_API = "https://www.bing.com/indexnow"


def load_key() -> str:
    if not KEY_FILE.is_file():
        raise FileNotFoundError(f"Key file not found: {KEY_FILE}")
    return KEY_FILE.read_text(encoding="utf-8").strip()


def load_sitemap_urls(limit: int = 100) -> list[str]:
    if not SITEMAP_FILE.is_file():
        raise FileNotFoundError(f"Sitemap file not found: {SITEMAP_FILE}")
    tree = ET.parse(SITEMAP_FILE)
    urls = [node.text.strip() for node in tree.findall(".//{*}loc") if node.text]
    return urls[:limit]


def submit_indexnow(urls: list[str], dry_run: bool = False) -> dict:
    key = load_key()
    key_location = f"https://{HOST}/{KEY_FILE.name}"
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": key_location,
        "urlList": urls
    }

    if dry_run:
        return {
            "status": "dry_run",
            "urls_count": len(urls),
            "payload": payload,
            "endpoints": [INDEXNOW_API, BING_API]
        }

    results = {}
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "SporlyWorks-IndexNow-Dispatcher/2.0"
    }

    for endpoint in (INDEXNOW_API, BING_API):
        req = Request(endpoint, data=data, headers=headers, method="POST")
        try:
            with urlopen(req, timeout=10) as resp:
                results[endpoint] = {
                    "code": resp.getcode(),
                    "msg": resp.reason
                }
        except HTTPError as e:
            results[endpoint] = {
                "code": e.code,
                "msg": str(e.reason)
            }
        except (URLError, TimeoutError) as e:
            results[endpoint] = {
                "error": str(e)
            }

    return {
        "status": "submitted",
        "urls_count": len(urls),
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(description="Submit URLs to IndexNow API")
    parser.add_argument("--dry-run", action="store_true", help="Simulate ping without sending HTTP requests")
    parser.add_argument("--urls", nargs="*", help="Explicit URLs to submit (defaults to sitemap.xml)")
    parser.add_argument("--limit", type=int, default=50, help="Max URLs to submit from sitemap (default: 50)")
    args = parser.parse_args()

    urls = args.urls if args.urls else load_sitemap_urls(limit=args.limit)
    print(f"Loaded {len(urls)} URLs for IndexNow submission")
    
    out = submit_indexnow(urls, dry_run=args.dry_run)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
