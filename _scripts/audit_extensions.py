#!/usr/bin/env python3
"""
Full extension portfolio quality audit.
Checks every Chrome extension for common issues.
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

issues = []
stats = {
    "total": 0,
    "mv3": 0,
    "mv2": 0,
    "has_icons": 0,
    "has_128_icon": 0,
    "has_homepage": 0,
    "has_background": 0,
    "has_popup": 0,
    "has_content_scripts": 0,
    "desc_too_long": 0,
    "desc_too_short": 0,
    "missing_icon_files": 0,
}

for item in sorted(os.listdir(REPO_ROOT)):
    full_path = os.path.join(REPO_ROOT, item)
    if not os.path.isdir(full_path):
        continue
    if item.startswith(('_', '.', 'node_modules', 'venv', 'CWS', 'build', 'dist')):
        continue
    if item.endswith('-firefox'):
        continue
    
    manifest_path = os.path.join(full_path, "manifest.json")
    if not os.path.exists(manifest_path):
        continue
    
    try:
        with open(manifest_path) as f:
            m = json.load(f)
    except json.JSONDecodeError as e:
        issues.append(f"❌ {item}/manifest.json: INVALID JSON — {e}")
        continue
    
    stats["total"] += 1
    
    # Check manifest version
    mv = m.get("manifest_version")
    if mv == 3:
        stats["mv3"] += 1
    elif mv == 2:
        stats["mv2"] += 1
        issues.append(f"⚠️  {item}: Still using Manifest V2 (should be V3)")
    
    # Check version format
    version = m.get("version", "")
    if not version:
        issues.append(f"❌ {item}: Missing version field")
    
    # Check description
    desc = m.get("description", "")
    if not desc:
        issues.append(f"❌ {item}: Missing description")
    elif len(desc) > 132:
        stats["desc_too_long"] += 1
        issues.append(f"⚠️  {item}: Description too long ({len(desc)} chars, max 132)")
    elif len(desc) < 10:
        stats["desc_too_short"] += 1
        issues.append(f"⚠️  {item}: Description too short ({len(desc)} chars)")
    
    # Check homepage_url
    if m.get("homepage_url"):
        stats["has_homepage"] += 1
    else:
        issues.append(f"⚠️  {item}: Missing homepage_url")
    
    # Check icons
    icons = m.get("icons", {})
    if icons:
        stats["has_icons"] += 1
        if "128" in icons:
            stats["has_128_icon"] += 1
            icon_path = os.path.join(full_path, icons["128"])
            if not os.path.exists(icon_path):
                stats["missing_icon_files"] += 1
                issues.append(f"❌ {item}: 128px icon file missing: {icons['128']}")
        else:
            issues.append(f"⚠️  {item}: No 128px icon defined")
    else:
        issues.append(f"❌ {item}: No icons defined")
    
    # Check popup
    action = m.get("action", m.get("browser_action", {}))
    if action and action.get("default_popup"):
        stats["has_popup"] += 1
        popup_path = os.path.join(full_path, action["default_popup"])
        if not os.path.exists(popup_path):
            issues.append(f"❌ {item}: Popup file missing: {action['default_popup']}")
    
    # Check background
    bg = m.get("background", {})
    if bg:
        stats["has_background"] += 1
        sw = bg.get("service_worker")
        if sw:
            sw_path = os.path.join(full_path, sw)
            if not os.path.exists(sw_path):
                issues.append(f"❌ {item}: Service worker file missing: {sw}")
    
    # Check content scripts
    cs = m.get("content_scripts", [])
    if cs:
        stats["has_content_scripts"] += 1
        for script_group in cs:
            for js_file in script_group.get("js", []):
                js_path = os.path.join(full_path, js_file)
                if not os.path.exists(js_path):
                    issues.append(f"❌ {item}: Content script file missing: {js_file}")
    
    # Check name length
    name = m.get("name", "")
    if len(name) > 45:
        issues.append(f"⚠️  {item}: Name too long ({len(name)} chars, CWS limit ~45)")

# Output
print("=" * 60)
print("      SporlyWorks Extension Portfolio Audit Report")
print("=" * 60)
print(f"\n📊 Statistics:")
print(f"   Total Chrome extensions: {stats['total']}")
print(f"   Manifest V3: {stats['mv3']}")
print(f"   Manifest V2: {stats['mv2']}")
print(f"   Has 128px icon: {stats['has_128_icon']}/{stats['total']}")
print(f"   Has homepage_url: {stats['has_homepage']}/{stats['total']}")
print(f"   Has popup: {stats['has_popup']}/{stats['total']}")
print(f"   Has background/SW: {stats['has_background']}/{stats['total']}")
print(f"   Has content scripts: {stats['has_content_scripts']}/{stats['total']}")

if issues:
    critical = [i for i in issues if i.startswith("❌")]
    warnings = [i for i in issues if i.startswith("⚠️")]
    
    print(f"\n🔴 Critical Issues ({len(critical)}):")
    for issue in critical:
        print(f"   {issue}")
    
    if warnings:
        print(f"\n🟡 Warnings ({len(warnings)}):")
        for issue in warnings:
            print(f"   {issue}")
else:
    print("\n✅ No issues found!")

print(f"\n{'=' * 60}")
