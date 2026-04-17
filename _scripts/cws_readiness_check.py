#!/usr/bin/env python3
"""
CWS Readiness Validator
========================
Pre-flight check for Chrome Web Store submission.
Validates that each flagship extension meets all CWS requirements:
  - manifest.json v3 compliance
  - Required fields (name, version, description, icons)
  - Popup HTML exists and loads correctly
  - License validator is wired
  - Brand palette is present
  - Icon files exist at required sizes

Usage:
    python3 cws_readiness_check.py
"""

import os
import json
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

FLAGSHIPS = [
    "api-tester-pro", "css-inspector-pro", "dom-editor-pro",
    "network-monitor-pro", "seo-content-pro", "form-filler-pro",
    "wcag-auditor", "privacy-scanner", "contract-highlighter",
    "invoice-extractor", "crm-data-extractor", "ai-content-bouncer",
    "llm-privacy-scrub", "amazon-fake-review-skimmer", "site-speed-analyzer",
]

REQUIRED_ICON_SIZES = ["16", "32", "48", "128"]


def check_extension(ext_name):
    """Run all CWS readiness checks on an extension. Returns (pass_count, fail_count, issues)."""
    ext_dir = os.path.join(REPO_ROOT, ext_name)
    issues = []
    passes = 0

    if not os.path.isdir(ext_dir):
        return 0, 1, [f"FATAL: Directory {ext_name}/ does not exist"]

    # 1. manifest.json exists and is valid JSON
    manifest_path = os.path.join(ext_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        issues.append("FATAL: manifest.json missing")
        return passes, len(issues), issues

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        passes += 1
    except json.JSONDecodeError as e:
        issues.append(f"FATAL: manifest.json invalid JSON: {e}")
        return passes, len(issues), issues

    # 2. Manifest version
    mv = manifest.get("manifest_version")
    if mv == 3:
        passes += 1
    elif mv == 2:
        issues.append("WARN: manifest_version is 2 (CWS prefers MV3)")
    else:
        issues.append(f"FAIL: manifest_version is {mv} (must be 2 or 3)")

    # 3. Required fields
    for field in ["name", "version", "description"]:
        val = manifest.get(field, "")
        if val and len(val) > 0:
            passes += 1
        else:
            issues.append(f"FAIL: Missing required field '{field}'")

    # 4. Description length (CWS requires <= 132 chars for short desc)
    desc = manifest.get("description", "")
    if len(desc) > 132:
        issues.append(f"WARN: description is {len(desc)} chars (CWS recommends <= 132)")
    elif len(desc) < 10:
        issues.append(f"WARN: description is very short ({len(desc)} chars)")
    else:
        passes += 1

    # 5. Icons
    icons = manifest.get("icons", {})
    for size in REQUIRED_ICON_SIZES:
        icon_path = icons.get(size, "")
        if icon_path:
            full_icon = os.path.join(ext_dir, icon_path)
            if os.path.isfile(full_icon):
                passes += 1
            else:
                issues.append(f"FAIL: Icon {size}px declared but file missing: {icon_path}")
        else:
            issues.append(f"FAIL: Missing icon size {size}px in manifest")

    # 6. Popup HTML
    popup_path = None
    action = manifest.get("action", manifest.get("browser_action", manifest.get("page_action", {})))
    if isinstance(action, dict):
        popup_path = action.get("default_popup", "")
    if popup_path:
        full_popup = os.path.join(ext_dir, popup_path)
        if os.path.isfile(full_popup):
            passes += 1
            # Check if license_validator.js is loaded
            with open(full_popup) as f:
                html = f.read()
            if "license_validator" in html:
                passes += 1
            else:
                issues.append("WARN: license_validator.js not loaded in popup HTML")
        else:
            issues.append(f"FAIL: Popup file declared but missing: {popup_path}")
    else:
        issues.append("WARN: No popup defined in manifest")

    # 7. Brand palette in CSS
    css_path = os.path.join(ext_dir, "popup", "popup.css")
    if os.path.isfile(css_path):
        with open(css_path) as f:
            css = f.read()
        if "--sporlyworks-" in css:
            passes += 1
        else:
            issues.append("WARN: Brand palette CSS variables not found")
    else:
        issues.append("WARN: popup/popup.css not found")

    # 8. Permissions check (alert on dangerous ones)
    perms = manifest.get("permissions", []) + manifest.get("optional_permissions", [])
    dangerous = [p for p in perms if p in ["<all_urls>", "tabs", "history", "bookmarks", "downloads"]]
    if dangerous:
        issues.append(f"INFO: Broad permissions detected: {dangerous} (may slow CWS review)")
    else:
        passes += 1

    # 9. Content scripts (check for overly broad matches)
    cs = manifest.get("content_scripts", [])
    for script_block in cs:
        matches = script_block.get("matches", [])
        if "<all_urls>" in matches or "*://*/*" in matches:
            issues.append("INFO: Content script matches all URLs (may slow CWS review)")

    return passes, len(issues), issues


def main():
    print("=" * 70)
    print("CWS READINESS VALIDATOR — Flagship Extensions")
    print("=" * 70)

    total_pass = 0
    total_fail = 0
    results = {}

    for ext in FLAGSHIPS:
        passes, fails, issues = check_extension(ext)
        total_pass += passes
        total_fail += fails
        results[ext] = {"passes": passes, "fails": fails, "issues": issues}

        status = "✅ READY" if fails == 0 else "⚠️ ISSUES" if all("WARN" in i or "INFO" in i for i in issues) else "❌ BLOCKED"
        print(f"\n{status} {ext} ({passes} passed, {fails} issues)")
        for issue in issues:
            print(f"     {issue}")

    print("\n" + "=" * 70)
    print(f"SUMMARY: {total_pass} checks passed, {total_fail} issues across {len(FLAGSHIPS)} extensions")

    ready = sum(1 for r in results.values() if r["fails"] == 0)
    soft_issues = sum(1 for r in results.values() if r["fails"] > 0 and all("WARN" in i or "INFO" in i for i in r["issues"]))
    blocked = len(FLAGSHIPS) - ready - soft_issues

    print(f"  ✅ Ready to ship: {ready}")
    print(f"  ⚠️ Soft issues (non-blocking): {soft_issues}")
    print(f"  ❌ Blocked: {blocked}")
    print("=" * 70)

    # Save report
    report_path = os.path.join(REPO_ROOT, "marketing", "cws_readiness_report.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull report: {report_path}")


if __name__ == "__main__":
    main()
