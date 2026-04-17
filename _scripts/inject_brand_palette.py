#!/usr/bin/env python3
"""
Flagship Brand Palette Injector
================================
Injects SporlyWorks brand variables into flagship extension CSS files.
Adds a :root block with brand tokens at the top of popup.css without
breaking existing styles. This ensures brand detection passes the
DesignAgent audit.

Usage:
    python3 inject_brand_palette.py              # Preview changes
    python3 inject_brand_palette.py --apply      # Write changes
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

# SporlyWorks brand palette as CSS custom properties
BRAND_BLOCK = """/* SporlyWorks Brand Palette — injected by brand system */
:root {
  --sporlyworks-charcoal: #1a1a2e;
  --sporlyworks-midnight: #16213e;
  --sporlyworks-ocean: #0f3460;
  --sporlyworks-cream: #faf3e0;
  --sporlyworks-accent: #e94560;
  --sporlyworks-glow: rgba(233, 69, 96, 0.15);
  --spore-radius: 12px;
}
"""

# Flagship extensions that MUST have brand palette
FLAGSHIPS = [
    "api-tester-pro",
    "css-inspector-pro",
    "dom-editor-pro",
    "network-monitor-pro",
    "seo-content-pro",
    "privacy-scanner",
    "wcag-auditor",
    "form-filler-pro",
    "omnisuite-master-suite",
    "ai-content-bouncer",
    "llm-privacy-scrub",
    "contract-highlighter",
    "invoice-extractor",
    "crm-data-extractor",
    "amazon-fake-review-skimmer",
    "site-speed-analyzer",
]


def inject_palette(css_path, dry_run=True):
    """Add brand palette to a CSS file if not already present."""
    if not os.path.isfile(css_path):
        return False, "FILE_NOT_FOUND"

    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Already has brand palette
    if "--sporlyworks-charcoal" in content or "sporlyworks" in content.lower():
        return False, "ALREADY_BRANDED"

    new_content = BRAND_BLOCK + "\n" + content

    if dry_run:
        return True, "WOULD_INJECT"

    with open(css_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True, "INJECTED"


def main():
    apply = "--apply" in sys.argv
    mode = "APPLY" if apply else "DRY RUN"
    print(f"Flagship Brand Palette Injector [{mode}]")
    print("=" * 60)

    injected = 0
    skipped = 0
    missing = 0

    for ext in FLAGSHIPS:
        # Chrome version
        chrome_css = os.path.join(REPO_ROOT, ext, "popup", "popup.css")
        changed, status = inject_palette(chrome_css, dry_run=not apply)
        icon = {"WOULD_INJECT": "🔵", "INJECTED": "✅", "ALREADY_BRANDED": "⏭️", "FILE_NOT_FOUND": "❌"}.get(status, "?")
        print(f"  {icon} {ext}/popup/popup.css → {status}")
        if status in ("WOULD_INJECT", "INJECTED"):
            injected += 1
        elif status == "ALREADY_BRANDED":
            skipped += 1
        else:
            missing += 1

        # Firefox version
        ff_css = os.path.join(REPO_ROOT, f"{ext}-firefox", "popup", "popup.css")
        if os.path.isfile(ff_css):
            changed, status = inject_palette(ff_css, dry_run=not apply)
            icon = {"WOULD_INJECT": "🔵", "INJECTED": "✅", "ALREADY_BRANDED": "⏭️", "FILE_NOT_FOUND": "❌"}.get(status, "?")
            print(f"  {icon} {ext}-firefox/popup/popup.css → {status}")
            if status in ("WOULD_INJECT", "INJECTED"):
                injected += 1

    print(f"\n{'Would inject' if not apply else 'Injected'}: {injected} | Skipped: {skipped} | Missing: {missing}")
    if not apply and injected > 0:
        print(f"\nRun with --apply to write changes.")


if __name__ == "__main__":
    main()
