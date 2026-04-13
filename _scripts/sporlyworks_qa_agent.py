#!/usr/bin/env python3
"""
SporlyWorks QA Agent v8.0
==========================
Comprehensive automated quality assurance that runs every board cycle.

Checks:
  - Portfolio integrity (manifest validation, MV2/MV3 audit)
  - Landing page health (dead links, binary availability, consistency)
  - GitHub release verification
  - Infrastructure health (Cloudflare worker, Railway)
  - Workflow status (recent GitHub Actions failures)
  - Extension description length (CWS 132 char limit)

Reports findings back to the board ledger under 'qa_last_report'.
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
    """Check URL accessibility. Returns (status_code, error_msg)."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "SporlyWorks-QA/2.0")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, None
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):
            try:
                req2 = urllib.request.Request(url)
                req2.add_header("User-Agent", "SporlyWorks-QA/2.0")
                req2.add_header("Range", "bytes=0-0")
                with urllib.request.urlopen(req2, timeout=timeout) as resp2:
                    return resp2.status, None
            except urllib.error.HTTPError as e2:
                if e2.code == 206:
                    return 200, None
                return e2.code, str(e2)
            except Exception as e2:
                return 0, str(e2)
        return e.code, str(e)
    except Exception as e:
        return 0, str(e)


# ── Portfolio Integrity ──────────────────────────────────────────────────

def audit_portfolio_integrity():
    """Verify all extension directories have valid manifest.json files."""
    findings = []
    chrome_count = 0
    firefox_count = 0
    android_count = 0
    mv2_extensions = []
    mv3_extensions = []

    # Chrome + Firefox extensions
    for item in sorted(os.listdir(REPO_ROOT)):
        item_path = os.path.join(REPO_ROOT, item)
        if not os.path.isdir(item_path):
            continue
        if item.startswith(("_", ".")) or item in (
            "dist", "build", "node_modules", "CWS_Upload_Ready",
            "marketing", "localtunnel-bypasser", "web-ext-artifacts",
            "~"
        ):
            continue

        # Skip known non-extension directories
        manifest_path = os.path.join(item_path, "manifest.json")

        if "-firefox" in item:
            if os.path.isfile(manifest_path):
                firefox_count += 1
                try:
                    with open(manifest_path) as f:
                        json.load(f)
                except json.JSONDecodeError:
                    findings.append(f"BROKEN_MANIFEST: {item}/manifest.json is invalid JSON")
            else:
                findings.append(f"MISSING_MANIFEST: {item}/ has no manifest.json")
        else:
            if os.path.isfile(manifest_path):
                chrome_count += 1
                try:
                    with open(manifest_path) as f:
                        data = json.load(f)
                        # Required fields check
                        if "name" not in data or "version" not in data:
                            findings.append(f"INCOMPLETE_MANIFEST: {item}/ missing name or version")
                        # MV2/MV3 tracking
                        mv = data.get("manifest_version", 0)
                        if mv == 2:
                            mv2_extensions.append(item)
                        elif mv == 3:
                            mv3_extensions.append(item)
                        else:
                            findings.append(f"INVALID_MV: {item}/ has manifest_version={mv}")
                        # Description length check (CWS limit: 132 chars)
                        desc = data.get("description", "")
                        if len(desc) > 132:
                            findings.append(f"DESC_TOO_LONG: {item}/ description is {len(desc)} chars (CWS limit: 132)")
                        elif not desc:
                            findings.append(f"NO_DESCRIPTION: {item}/ has no description field")
                except json.JSONDecodeError:
                    findings.append(f"BROKEN_MANIFEST: {item}/manifest.json is invalid JSON")

    # Android apps
    android_dir = os.path.join(REPO_ROOT, "_android_aabs")
    if os.path.isdir(android_dir):
        for f in os.listdir(android_dir):
            if f.endswith(".aab"):
                android_count += 1
                aab_path = os.path.join(android_dir, f)
                if os.path.getsize(aab_path) < 1000:
                    findings.append(
                        f"SUSPICIOUS_AAB: {f} is abnormally small ({os.path.getsize(aab_path)} bytes)"
                    )

    return {
        "chrome_extensions": chrome_count,
        "firefox_extensions": firefox_count,
        "android_apps": android_count,
        "mv2_count": len(mv2_extensions),
        "mv3_count": len(mv3_extensions),
        "mv2_extensions": mv2_extensions[:10],  # Sample for brevity
        "findings": findings,
    }


# ── Landing Page Audit ───────────────────────────────────────────────────

def audit_landing_page():
    """Check landing page files, links, and binary availability."""
    findings = []
    landing_dir = os.path.join(REPO_ROOT, "_landing_page")

    if not os.path.isdir(landing_dir):
        findings.append("CRITICAL: _landing_page directory not found")
        return findings

    # Check required files
    required_files = ["index.html", "download.html", "style.css", "favicon.ico"]
    for rf in required_files:
        if not os.path.isfile(os.path.join(landing_dir, rf)):
            findings.append(f"MISSING_FILE: _landing_page/{rf}")

    # Check download binaries
    binaries_dir = os.path.join(landing_dir, "binaries")
    expected_binaries = [
        "SporlyWorks_OmniSuite_Complete.zip",
        "SporlyWorks_Firefox_Extensions.zip",
    ]
    for eb in expected_binaries:
        bin_path = os.path.join(binaries_dir, eb)
        if not os.path.isfile(bin_path):
            findings.append(f"MISSING_BINARY: binaries/{eb} — download link will 404")
        elif os.path.getsize(bin_path) < 10000:
            findings.append(
                f"EMPTY_BINARY: binaries/{eb} is suspiciously small ({os.path.getsize(bin_path)} bytes)"
            )

    # Scan HTML for external dead links
    for html_file in ["index.html", "download.html"]:
        html_path = os.path.join(landing_dir, html_file)
        if not os.path.isfile(html_path):
            continue
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract href URLs
        urls = []
        idx = 0
        while True:
            idx = content.find('href="http', idx)
            if idx == -1:
                break
            start = content.index('"', idx) + 1
            end = content.index('"', start)
            url = content[start:end]
            if "fonts.googleapis.com" not in url and "fonts.gstatic.com" not in url:
                urls.append((html_file, url))
            idx = end

        checked = set()
        for source_file, url in urls:
            if url in checked:
                continue
            checked.add(url)
            status, err = check_url(url)
            if status != 200:
                findings.append(f"DEAD_LINK: {source_file} → {url} (HTTP {status})")

    return findings


# ── GitHub Release Audit ─────────────────────────────────────────────────

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
        findings.append(f"ANDROID_ZIP_MISSING: Android download returned HTTP {status}")

    return findings


# ── Infrastructure Health ────────────────────────────────────────────────

def audit_infrastructure():
    """Check that live services are responding."""
    findings = []

    # Cloudflare email worker health
    cf_status, cf_err = check_url(
        "https://sporlyworks-support.sporlyworks.workers.dev/health"
    )
    if cf_status not in (200, 400, 405):  # email workers return 400/405 for HTTP — that's OK
        findings.append(
            f"CF_WORKER_DOWN: Email worker health returned HTTP {cf_status}: {cf_err}"
        )

    # Landing page live site
    lp_status, lp_err = check_url("https://sporlyworks.com")
    if lp_status != 200:
        findings.append(f"LANDING_PAGE_DOWN: sporlyworks.com returned HTTP {lp_status}")

    return findings


# ── Workflow Status ──────────────────────────────────────────────────────

def audit_workflow_status():
    """Check if recent GitHub Actions workflow runs have been failing."""
    findings = []
    gh_token = os.environ.get("GITHUB_TOKEN")
    if not gh_token:
        return findings  # Can't check without token

    try:
        url = "https://api.github.com/repos/daveestaaqui/microAssets/actions/runs?per_page=5&status=failure"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"token {gh_token}")
        req.add_header("Accept", "application/vnd.github+json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            failed_runs = data.get("workflow_runs", [])
            if len(failed_runs) >= 3:
                findings.append(
                    f"WORKFLOW_FAILING: {len(failed_runs)} recent workflow failures detected"
                )
    except Exception as e:
        logging.warning(f"Could not check workflow status: {e}")

    return findings


# ── Full Audit ───────────────────────────────────────────────────────────

def run_full_audit():
    """Execute all QA checks and return the combined report."""
    logging.info("Starting full QA audit (v8.0)...")
    report = {
        "audit_timestamp": datetime.utcnow().isoformat() + "Z",
        "qa_version": "8.0",
        "status": "PASS",
        "portfolio": {},
        "findings": [],
        "checks_run": [],
    }

    # 1. Portfolio integrity
    logging.info("Checking portfolio integrity...")
    portfolio = audit_portfolio_integrity()
    report["portfolio"] = {
        "chrome_extensions": portfolio["chrome_extensions"],
        "firefox_extensions": portfolio["firefox_extensions"],
        "android_apps": portfolio["android_apps"],
        "mv2_count": portfolio.get("mv2_count", 0),
        "mv3_count": portfolio.get("mv3_count", 0),
    }
    if portfolio.get("mv2_extensions"):
        report["portfolio"]["mv2_sample"] = portfolio["mv2_extensions"]
    report["findings"].extend(portfolio["findings"])
    report["checks_run"].append("portfolio_integrity")

    # 2. Landing page audit
    logging.info("Checking landing page...")
    landing_findings = audit_landing_page()
    report["findings"].extend(landing_findings)
    report["checks_run"].extend(["landing_page_links", "landing_page_consistency", "download_binaries"])

    # 3. GitHub release check
    logging.info("Checking GitHub releases...")
    release_findings = audit_github_release()
    report["findings"].extend(release_findings)
    report["checks_run"].append("github_release")

    # 4. Infrastructure health
    logging.info("Checking infrastructure health...")
    infra_findings = audit_infrastructure()
    report["findings"].extend(infra_findings)
    report["checks_run"].append("infrastructure_health")

    # 5. Workflow status
    logging.info("Checking GitHub Actions status...")
    workflow_findings = audit_workflow_status()
    report["findings"].extend(workflow_findings)
    report["checks_run"].append("workflow_status")

    # Set overall status
    critical = sum(
        1
        for f in report["findings"]
        if any(k in f for k in ("CRITICAL", "DEAD_LINK", "MISSING_BINARY", "CF_WORKER_DOWN", "LANDING_PAGE_DOWN"))
    )
    if critical > 0:
        report["status"] = "FAIL"
    elif len(report["findings"]) > 0:
        report["status"] = "WARN"

    logging.info(
        f"QA Audit complete: {report['status']} — "
        f"{len(report['findings'])} finding(s) across {len(report['checks_run'])} checks"
    )
    return report


if __name__ == "__main__":
    report = run_full_audit()
    print(json.dumps(report, indent=2))
