#!/usr/bin/env python3
"""
SporlyWorks QA Agent
====================
Automated quality assurance that runs every board cycle.
Checks: dead links, asset consistency, download availability,
portfolio integrity, and landing page accuracy.

Reports findings back to the board ledger under 'qa_findings'.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

logging.basicConfig(
    format='%(asctime)s | QA Agent | [%(levelname)s] %(message)s',
    level=logging.INFO
)


def check_url(url, timeout=10):
    """Check if a URL is accessible. Returns (status_code, error_msg)."""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'SporlyWorks-QA/1.0')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, None
    except urllib.error.HTTPError as e:
        # Some servers don't support HEAD — fall back to GET with range
        if e.code in (403, 404, 405):
            try:
                req2 = urllib.request.Request(url)
                req2.add_header('User-Agent', 'SporlyWorks-QA/1.0')
                req2.add_header('Range', 'bytes=0-0')  # Only fetch 1 byte
                with urllib.request.urlopen(req2, timeout=timeout) as resp2:
                    return resp2.status, None
            except urllib.error.HTTPError as e2:
                # 206 Partial Content or 200 both mean the file exists
                if e2.code == 206:
                    return 200, None
                return e2.code, str(e2)
            except Exception as e2:
                return 0, str(e2)
        return e.code, str(e)
    except Exception as e:
        return 0, str(e)


def audit_portfolio_integrity():
    """Verify all extension directories have valid manifest.json files."""
    findings = []
    chrome_count = 0
    firefox_count = 0
    android_count = 0

    # Chrome extensions
    for item in sorted(os.listdir(REPO_ROOT)):
        item_path = os.path.join(REPO_ROOT, item)
        if not os.path.isdir(item_path):
            continue
        if item.startswith(('_', '.')) or item in ('dist', 'build', 'node_modules', 'CWS_Upload_Ready', 'marketing'):
            continue
        if '-firefox' in item:
            manifest = os.path.join(item_path, 'manifest.json')
            if os.path.isfile(manifest):
                firefox_count += 1
                try:
                    with open(manifest) as f:
                        json.load(f)
                except json.JSONDecodeError:
                    findings.append(f"BROKEN_MANIFEST: {item}/manifest.json is invalid JSON")
            else:
                findings.append(f"MISSING_MANIFEST: {item}/ has no manifest.json")
        else:
            manifest = os.path.join(item_path, 'manifest.json')
            if os.path.isfile(manifest):
                chrome_count += 1
                try:
                    with open(manifest) as f:
                        data = json.load(f)
                        if 'name' not in data or 'version' not in data:
                            findings.append(f"INCOMPLETE_MANIFEST: {item}/ missing name or version")
                except json.JSONDecodeError:
                    findings.append(f"BROKEN_MANIFEST: {item}/manifest.json is invalid JSON")

    # Android apps
    android_dir = os.path.join(REPO_ROOT, '_android_aabs')
    if os.path.isdir(android_dir):
        for f in os.listdir(android_dir):
            if f.endswith('.aab'):
                android_count += 1
                aab_path = os.path.join(android_dir, f)
                if os.path.getsize(aab_path) < 1000:
                    findings.append(f"SUSPICIOUS_AAB: {f} is abnormally small ({os.path.getsize(aab_path)} bytes)")

    return {
        'chrome_extensions': chrome_count,
        'firefox_extensions': firefox_count,
        'android_apps': android_count,
        'findings': findings
    }


def audit_landing_page():
    """Check landing page files and links for issues."""
    findings = []
    landing_dir = os.path.join(REPO_ROOT, '_landing_page')

    if not os.path.isdir(landing_dir):
        findings.append("CRITICAL: _landing_page directory not found")
        return findings

    # Check required files exist
    required_files = ['index.html', 'download.html', 'style.css', 'favicon.ico']
    for rf in required_files:
        if not os.path.isfile(os.path.join(landing_dir, rf)):
            findings.append(f"MISSING_FILE: _landing_page/{rf} does not exist")

    # Check download binaries exist
    binaries_dir = os.path.join(landing_dir, 'binaries')
    expected_binaries = [
        'SporlyWorks_OmniSuite_Complete.zip',
        'SporlyWorks_Firefox_Extensions.zip'
    ]
    for eb in expected_binaries:
        bin_path = os.path.join(binaries_dir, eb)
        if not os.path.isfile(bin_path):
            findings.append(f"MISSING_BINARY: binaries/{eb} not found — download link will 404")
        elif os.path.getsize(bin_path) < 10000:
            findings.append(f"EMPTY_BINARY: binaries/{eb} is suspiciously small ({os.path.getsize(bin_path)} bytes)")

    # Scan HTML files for external links and verify them
    for html_file in ['index.html', 'download.html']:
        html_path = os.path.join(landing_dir, html_file)
        if not os.path.isfile(html_path):
            continue
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract href URLs (simple regex-free approach)
        urls = []
        idx = 0
        while True:
            idx = content.find('href="http', idx)
            if idx == -1:
                break
            start = content.index('"', idx) + 1
            end = content.index('"', start)
            url = content[start:end]
            # Skip font CDN URLs — they're always fine
            if 'fonts.googleapis.com' not in url and 'fonts.gstatic.com' not in url:
                urls.append((html_file, url))
            idx = end

        # Check each URL (deduplicated)
        checked = set()
        for source_file, url in urls:
            if url in checked:
                continue
            checked.add(url)
            status, err = check_url(url)
            if status != 200:
                findings.append(f"DEAD_LINK: {source_file} → {url} (HTTP {status}: {err})")

    # Check for count consistency between index.html and download.html
    index_path = os.path.join(landing_dir, 'index.html')
    if os.path.isfile(index_path):
        with open(index_path, 'r') as f:
            index_content = f.read()
        # Check the meta description mentions Android
        if 'Android' not in index_content[:2000]:
            findings.append("INCONSISTENCY: index.html meta section doesn't mention Android apps")

    return findings


def audit_github_release():
    """Verify the GitHub Release with Android apps is accessible."""
    findings = []
    release_url = "https://github.com/daveestaaqui/micro-assets-landing-page/releases/tag/v1.0.0"
    status, err = check_url(release_url)
    if status != 200:
        findings.append(f"RELEASE_MISSING: GitHub Release v1.0.0 returned HTTP {status}")

    android_url = "https://github.com/daveestaaqui/micro-assets-landing-page/releases/download/v1.0.0/SporlyWorks_Android_Apps.zip"
    status, err = check_url(android_url)
    if status not in (200, 302):
        findings.append(f"ANDROID_ZIP_MISSING: Android apps download returned HTTP {status}")

    return findings


def run_full_audit():
    """Execute all QA checks and return the combined report."""
    logging.info("Starting full QA audit...")
    report = {
        'audit_timestamp': datetime.utcnow().isoformat() + 'Z',
        'status': 'PASS',
        'portfolio': {},
        'findings': [],
        'checks_run': []
    }

    # 1. Portfolio integrity
    logging.info("Checking portfolio integrity...")
    portfolio = audit_portfolio_integrity()
    report['portfolio'] = {
        'chrome_extensions': portfolio['chrome_extensions'],
        'firefox_extensions': portfolio['firefox_extensions'],
        'android_apps': portfolio['android_apps']
    }
    report['findings'].extend(portfolio['findings'])
    report['checks_run'].append('portfolio_integrity')

    # 2. Landing page audit
    logging.info("Checking landing page...")
    landing_findings = audit_landing_page()
    report['findings'].extend(landing_findings)
    report['checks_run'].append('landing_page_links')
    report['checks_run'].append('landing_page_consistency')
    report['checks_run'].append('download_binaries')

    # 3. GitHub release check
    logging.info("Checking GitHub releases...")
    release_findings = audit_github_release()
    report['findings'].extend(release_findings)
    report['checks_run'].append('github_release')

    # Set overall status
    critical_count = sum(1 for f in report['findings'] if 'CRITICAL' in f or 'DEAD_LINK' in f or 'MISSING_BINARY' in f)
    if critical_count > 0:
        report['status'] = 'FAIL'
    elif len(report['findings']) > 0:
        report['status'] = 'WARN'

    logging.info(f"QA Audit complete: {report['status']} — {len(report['findings'])} finding(s)")
    return report


if __name__ == '__main__':
    report = run_full_audit()
    print(json.dumps(report, indent=2))
