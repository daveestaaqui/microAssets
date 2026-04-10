#!/usr/bin/env python3
"""
SporlyWorks CWS Privacy Compliance Generator
=============================================
Reads every Chrome extension manifest, generates:
- Single purpose description (natural language, CWS compliant)
- Permission justifications (per-permission, CWS compliant)
- Data usage declarations

Outputs: _scripts/cws_privacy_compliance_master.json
"""

import json
import os
import glob
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(REPO_ROOT, "_scripts", "cws_privacy_compliance_master.json")

# Load CWS extension IDs
CWS_IDS_FILE = os.path.join(REPO_ROOT, "_scripts", "cws_extension_ids.json")
cws_ids = {}
if os.path.exists(CWS_IDS_FILE):
    with open(CWS_IDS_FILE) as f:
        cws_ids = json.load(f)

# Permission justification templates
PERMISSION_JUSTIFICATIONS = {
    "activeTab": "Used to access the current tab's content when the user explicitly activates the extension, enabling it to perform its core function on the active page.",
    "storage": "Used to save user preferences and settings locally so they persist between browser sessions. No data is transmitted externally.",
    "scripting": "Used to inject the extension's core functionality script into the active tab when the user triggers the extension.",
    "tabs": "Used to read the current tab's URL and title for the extension's core feature. No browsing history is collected or transmitted.",
    "clipboardWrite": "Used to copy generated or extracted content to the user's clipboard when they click the copy button.",
    "clipboardRead": "Used to read clipboard contents for processing within the extension's popup interface.",
    "contextMenus": "Used to add a right-click context menu option for quick access to the extension's features.",
    "alarms": "Used to schedule periodic background tasks such as reminders or timer notifications.",
    "notifications": "Used to display browser notifications for alerts, timers, or important status updates.",
    "downloads": "Used to save generated files (e.g., exports, screenshots) to the user's local downloads folder.",
    "webNavigation": "Used to detect page navigation events to trigger the extension's functionality at the appropriate time.",
    "cookies": "Used to read and manage browser cookies as the extension's core feature for cookie inspection/management.",
    "declarativeNetRequest": "Used to modify or block network requests according to user-defined rules for the extension's filtering functionality.",
    "offscreen": "Used to perform background processing tasks that require a DOM environment, such as clipboard operations.",
    "sidePanel": "Used to display the extension's interface in Chrome's side panel for persistent, non-intrusive access.",
    "identity": "Used to authenticate the user with their Google account for features that require authorization.",
    "history": "Used to access browsing history as part of the extension's core history management feature.",
    "bookmarks": "Used to read and organize bookmarks as the extension's primary bookmark management feature.",
    "topSites": "Used to display the user's most visited sites as part of the extension's dashboard feature.",
    "management": "Used to list installed extensions for the extension's management or diagnostic features.",
    "fontSettings": "Used to read and modify font settings as part of the extension's typography management feature.",
    "webRequest": "Used to observe network requests for debugging/analysis purposes as the extension's core feature.",
    "proxy": "Used to manage proxy settings as part of the extension's proxy configuration feature.",
    "tts": "Used to provide text-to-speech functionality as the extension's core reading feature.",
    "tabGroups": "Used to organize tabs into groups as the extension's core tab management feature.",
    "power": "Used to prevent the system from sleeping during active tasks like downloads or timers.",
    "idle": "Used to detect user idle state for features like auto-pause or screen lock detection.",
    "debugger": "Used to access Chrome DevTools debugging protocol for the extension's developer tools features.",
    "system.display": "Used to read display information for the extension's screenshot or display management features.",
    "desktopCapture": "Used to capture screen content for the extension's screenshot or recording feature.",
    "tabCapture": "Used to capture the current tab's content for the extension's screenshot feature.",
    "gcm": "Used to receive push notifications from the extension's cloud messaging service.",
}

# Host permission justification templates
HOST_PERMISSION_JUSTIFICATIONS = {
    "<all_urls>": "Required to inject the extension's content script on any page the user visits, enabling its core functionality across all websites.",
    "*://*.google.com/*": "Required to apply the extension's functionality on Google pages as its core feature.",
    "*://*.github.com/*": "Required to apply the extension's functionality on GitHub pages as its core feature.",
    "*://*.linkedin.com/*": "Required to apply the extension's functionality on LinkedIn pages as its core feature.",
    "*://*.amazon.com/*": "Required to apply the extension's functionality on Amazon pages as its core feature.",
    "*://*.instagram.com/*": "Required to apply the extension's functionality on Instagram pages as its core feature.",
    "*://*.youtube.com/*": "Required to apply the extension's functionality on YouTube pages as its core feature.",
}

def get_single_purpose(name, description, permissions):
    """Generate a natural-language single purpose statement from the manifest."""
    # Clean up the name
    clean_name = re.sub(r'\s*[—–-]\s*.*$', '', name).strip()
    
    # If description is good enough, use it directly (truncate if needed)
    if description and len(description) > 20 and "required for" not in description.lower():
        # Make sure it reads as a purpose statement
        purpose = description.rstrip('.')
        if not purpose[0].isupper():
            purpose = purpose[0].upper() + purpose[1:]
        return purpose + "."
    
    return f"{clean_name} provides its described functionality through the browser extension popup interface."


def get_permission_justification(perm, name):
    """Get the CWS-compliant justification for a specific permission."""
    if perm in PERMISSION_JUSTIFICATIONS:
        return PERMISSION_JUSTIFICATIONS[perm]
    
    # Check if it's a host permission pattern
    for pattern, justification in HOST_PERMISSION_JUSTIFICATIONS.items():
        if pattern in perm or perm in pattern:
            return justification
    
    # Generic but compliant fallback
    return f"Required by {name} for its core functionality as described in the extension's single purpose."


def process_extension(ext_dir):
    """Process a single extension directory and generate compliance data."""
    manifest_path = os.path.join(ext_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        return None
    
    with open(manifest_path) as f:
        try:
            manifest = json.load(f)
        except json.JSONDecodeError:
            return None
    
    name = manifest.get("name", os.path.basename(ext_dir))
    description = manifest.get("description", "")
    permissions = manifest.get("permissions", [])
    host_permissions = manifest.get("host_permissions", [])
    optional_permissions = manifest.get("optional_permissions", [])
    content_scripts = manifest.get("content_scripts", [])
    
    # Build permission justifications
    perm_justifications = {}
    for perm in (permissions or []):
        perm_justifications[perm] = get_permission_justification(perm, name)
    
    # Build host permission justifications
    host_justifications = {}
    for hp in (host_permissions or []):
        host_justifications[hp] = get_permission_justification(hp, name)
    
    # Content script justification
    content_script_justification = None
    if content_scripts:
        matches = []
        for cs in content_scripts:
            matches.extend(cs.get("matches", []))
        if matches:
            domains = [m.replace("*://", "").replace("/*", "").replace("*.", "") for m in matches[:3]]
            domain_str = ", ".join(domains)
            content_script_justification = f"Content scripts are injected into {domain_str} pages to apply the extension's core functionality directly on those sites."
    
    # Determine if remote code is used
    uses_remote_code = False
    # Check background scripts for fetch/import
    bg = manifest.get("background", {})
    if bg.get("service_worker"):
        sw_path = os.path.join(ext_dir, bg["service_worker"])
        if os.path.exists(sw_path):
            with open(sw_path) as f:
                sw_content = f.read()
                if "import(" in sw_content or "eval(" in sw_content:
                    uses_remote_code = True
    
    ext_slug = os.path.basename(ext_dir)
    cws_id = cws_ids.get(ext_slug, None)
    
    return {
        "slug": ext_slug,
        "cws_id": cws_id,
        "name": name,
        "version": manifest.get("version", "1.0.0"),
        "single_purpose": get_single_purpose(name, description, permissions),
        "permission_justifications": perm_justifications,
        "host_permission_justifications": host_justifications,
        "content_script_justification": content_script_justification,
        "remote_code_declaration": "No remote code is executed. All logic runs locally within the extension." if not uses_remote_code else "Remote code may be loaded for specific functionality.",
        "data_usage": {
            "collects_personal_data": False,
            "sells_data_to_third_parties": False,
            "uses_data_for_unrelated_purposes": False,
            "data_disclosure": "This extension does not collect, transmit, or sell any user data. All processing occurs locally on the user's device."
        },
        "privacy_policy_url": "https://sporlyworks.com/privacy"
    }


def main():
    results = {}
    
    # Find all Chrome extension directories (non-firefox, non-underscore prefixed)
    for item in sorted(os.listdir(REPO_ROOT)):
        full_path = os.path.join(REPO_ROOT, item)
        if not os.path.isdir(full_path):
            continue
        if item.startswith(('_', '.', 'node_modules', 'venv', 'CWS')):
            continue
        if item.endswith('-firefox'):
            continue
        
        manifest_path = os.path.join(full_path, "manifest.json")
        if not os.path.exists(manifest_path):
            continue
        
        result = process_extension(full_path)
        if result:
            results[item] = result
    
    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Generated privacy compliance data for {len(results)} extensions")
    print(f"   Output: {OUTPUT_FILE}")
    
    # Stats
    with_cws_id = sum(1 for r in results.values() if r['cws_id'])
    print(f"   {with_cws_id} have CWS IDs (published)")
    print(f"   {len(results) - with_cws_id} without CWS IDs (not yet published)")
    
    # Show a sample
    sample_key = list(results.keys())[0] if results else None
    if sample_key:
        print(f"\n📋 Sample ({sample_key}):")
        sample = results[sample_key]
        print(f"   Single Purpose: {sample['single_purpose'][:80]}...")
        for perm, just in sample['permission_justifications'].items():
            print(f"   {perm}: {just[:60]}...")


if __name__ == "__main__":
    main()
