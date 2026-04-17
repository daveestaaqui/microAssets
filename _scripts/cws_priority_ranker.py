#!/usr/bin/env python3
"""
CWS Priority Ranker — Revenue-Weighted Queue Reordering
========================================================
Replaces FIFO CWS submission ordering with priority scoring based on:
  - Market category (dev tools > social utilities)
  - Monetization readiness (Pro Suite candidate bonus)
  - Competitive gap (unique tools rank higher than commodity ones)
  - Name recognition (clear, descriptive names rank higher)

Usage:
    python3 cws_priority_ranker.py              # Preview reordered queue
    python3 cws_priority_ranker.py --apply       # Rewrite cws_submission_queue.json
"""

import os
import json
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
QUEUE_FILE = os.path.join(REPO_ROOT, "cws_submission_queue.json")

# ── Priority Scoring ────────────────────────────────────────────────────

# Category scores: higher = more monetizable market
CATEGORY_SCORES = {
    "dev_tools":    90,   # Developer tools have highest B2B willingness-to-pay
    "seo":          85,   # SEO/marketing tools target businesses
    "security":     80,   # Security/privacy tools command premium pricing
    "productivity": 70,   # General productivity — large market, moderate WTP
    "design":       65,   # Design tools — niche but loyal users
    "social":       40,   # Social media tools — large audience, low WTP
    "utility":      50,   # Generic utilities — commodity, hard to monetize
    "fun":          30,   # Entertainment — high volume, near-zero WTP
}

# Map each extension to a category
EXTENSION_CATEGORIES = {
    # Dev tools (highest priority)
    "api-tester-pro": "dev_tools",
    "json-formatter": "dev_tools",
    "json-csv-converter": "dev_tools",
    "json-path-finder": "dev_tools",
    "jwt-decoder": "dev_tools",
    "regex-tester": "dev_tools",
    "diff-viewer": "dev_tools",
    "diff-checker": "dev_tools",
    "http-headers": "dev_tools",
    "http-status-checker": "dev_tools",
    "base64-encoder": "dev_tools",
    "url-encoder-decoder": "dev_tools",
    "dom-editor-pro": "dev_tools",
    "code-snippet-manager": "dev_tools",
    "github-line-numbers": "dev_tools",
    "github-quick-stats": "dev_tools",
    "network-monitor-pro": "dev_tools",

    # SEO & Marketing
    "page-seo-analyzer": "seo",
    "seo-content-pro": "seo",
    "og-previewer": "seo",
    "meta-tag-editor": "seo",
    "robots-viewer": "seo",
    "site-speed-analyzer": "seo",
    "whois-lookup": "seo",
    "wcag-auditor": "seo",
    "html-table-extractor": "seo",

    # Security & Privacy
    "privacy-scanner": "security",
    "cookie-manager": "security",
    "cookie-banner-rejector": "security",
    "user-agent-switcher": "security",
    "ai-content-bouncer": "security",
    "llm-privacy-scrub": "security",
    "amazon-fake-review-skimmer": "security",
    "contract-highlighter": "security",

    # Design
    "css-gradient-generator": "design",
    "css-flexbox-generator": "design",
    "css-grid-generator": "design",
    "css-box-shadow": "design",
    "css-inspector-pro": "design",
    "css-minifier": "design",
    "color-palette-generator": "design",
    "color-picker-eyedropper": "design",
    "font-identifier": "design",
    "favicon-grabber": "design",
    "responsive-viewer": "design",
    "page-ruler": "design",

    # Productivity
    "quick-notepad": "productivity",
    "quick-note-taker": "productivity",
    "pomodoro-anywhere": "productivity",
    "bookmark-manager": "productivity",
    "tab-suspender": "productivity",
    "tab-groups-saver": "productivity",
    "clipboard-history": "productivity",
    "reading-mode": "productivity",
    "time-tracker": "productivity",
    "form-filler-pro": "productivity",
    "email-template-builder": "productivity",
    "copy-as-markdown": "productivity",
    "invoice-extractor": "productivity",
    "crm-data-extractor": "productivity",
    "word-counter": "productivity",
    "text-case-converter": "productivity",
    "markdown-preview": "productivity",
    "wayback-machine-quick": "productivity",

    # Social
    "linkedin-hide-feed": "social",
    "instagram-clean-feed": "social",
    "reddit-redirect": "social",
    "sponsor-skipper": "social",
    "amazon-wide-mode": "social",
    "gdocs-focus-mode": "social",
    "meet-zoom-automute": "social",
    "jira-declutter": "social",
    "google-dark-search": "social",

    # Utility
    "dark-mode-everywhere": "utility",
    "qr-code-generator": "utility",
    "password-generator": "utility",
    "screenshot-capture": "utility",
    "hash-generator": "utility",
    "lorem-ipsum-generator": "utility",
    "link-checker": "utility",
    "timestamp-converter": "utility",
    "reading-time-badge": "utility",
    "url-shortener": "utility",
    "carbon-footprint-checker": "utility",
    "network-speed-test": "utility",
    "website-monitor-pro": "utility",

    # Master suite (special)
    "omnisuite-master-suite": "dev_tools",
}

# Pro Suite candidates get a bonus (these are the flagship monetization targets)
PRO_SUITE_CANDIDATES = {
    "css-inspector-pro", "network-monitor-pro", "seo-content-pro",
    "site-speed-analyzer", "api-tester-pro", "dom-editor-pro",
    "privacy-scanner", "wcag-auditor", "website-monitor-pro",
    "form-filler-pro", "omnisuite-master-suite",
}

# Unique/differentiated tools get a competitive gap bonus
UNIQUE_TOOLS = {
    "ai-content-bouncer", "llm-privacy-scrub", "amazon-fake-review-skimmer",
    "contract-highlighter", "invoice-extractor", "crm-data-extractor",
    "sponsor-skipper", "wcag-auditor", "omnisuite-master-suite",
}


def score_extension(name):
    """Calculate a priority score for an extension."""
    category = EXTENSION_CATEGORIES.get(name, "utility")
    base = CATEGORY_SCORES.get(category, 50)

    # Pro Suite bonus: +20 (these drive direct revenue)
    pro_bonus = 20 if name in PRO_SUITE_CANDIDATES else 0

    # Uniqueness bonus: +15 (less competition = faster install growth)
    unique_bonus = 15 if name in UNIQUE_TOOLS else 0

    # Name clarity bonus: +5 for "pro" in name (signals premium positioning)
    name_bonus = 5 if "pro" in name.lower() else 0

    return base + pro_bonus + unique_bonus + name_bonus


def rank_queue():
    """Load, score, sort, and return the reordered queue."""
    if not os.path.isfile(QUEUE_FILE):
        print("ERROR: cws_submission_queue.json not found")
        return None

    with open(QUEUE_FILE) as f:
        queue = json.load(f)

    # Collect all extensions across all waves
    all_extensions = []
    for wave_name, wave_data in queue.get("waves", {}).items():
        for ext in wave_data.get("items", []):
            all_extensions.append(ext)

    # Deduplicate
    all_extensions = list(dict.fromkeys(all_extensions))

    # Score and sort
    scored = [(ext, score_extension(ext)) for ext in all_extensions]
    scored.sort(key=lambda x: x[1], reverse=True)

    return queue, scored


def preview():
    """Print the reordered queue without modifying the file."""
    result = rank_queue()
    if not result:
        return
    queue, scored = result

    print("=" * 70)
    print("CWS PRIORITY QUEUE — Revenue-Weighted Ranking")
    print("=" * 70)
    print(f"{'Rank':<6}{'Extension':<40}{'Score':<8}{'Category':<15}")
    print("-" * 70)
    for i, (ext, score) in enumerate(scored, 1):
        cat = EXTENSION_CATEGORIES.get(ext, "utility")
        flags = []
        if ext in PRO_SUITE_CANDIDATES:
            flags.append("PRO")
        if ext in UNIQUE_TOOLS:
            flags.append("UNIQUE")
        flag_str = f" [{','.join(flags)}]" if flags else ""
        print(f"{i:<6}{ext:<40}{score:<8}{cat:<15}{flag_str}")

    # Show wave allocation recommendation
    print("\n" + "=" * 70)
    print("RECOMMENDED WAVE ALLOCATION (20 slots max)")
    print("=" * 70)
    wave_size = queue.get("config", {}).get("max_slots", 20)
    for wave_num in range(1, (len(scored) // wave_size) + 2):
        start = (wave_num - 1) * wave_size
        end = min(start + wave_size, len(scored))
        if start >= len(scored):
            break
        wave_exts = scored[start:end]
        avg_score = sum(s for _, s in wave_exts) / len(wave_exts) if wave_exts else 0
        print(f"\nWave {wave_num} (avg score: {avg_score:.0f}):")
        for ext, score in wave_exts:
            print(f"  {ext} ({score})")


def apply():
    """Rewrite the queue file with priority-ordered waves."""
    result = rank_queue()
    if not result:
        return
    queue, scored = result

    wave_size = queue.get("config", {}).get("max_slots", 20)
    new_waves = {}
    for wave_num in range(1, (len(scored) // wave_size) + 2):
        start = (wave_num - 1) * wave_size
        end = min(start + wave_size, len(scored))
        if start >= len(scored):
            break
        new_waves[f"wave_{wave_num}"] = {
            "items": [ext for ext, _ in scored[start:end]],
            "priority_scores": {ext: score for ext, score in scored[start:end]},
        }

    queue["waves"] = new_waves
    queue["config"]["priority_ranked"] = True
    queue["config"]["ranked_at"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"

    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)

    print(f"✅ Queue rewritten with {len(new_waves)} priority-ordered waves")
    print(f"   Top 5: {', '.join(ext for ext, _ in scored[:5])}")


if __name__ == "__main__":
    if "--apply" in sys.argv:
        apply()
    else:
        preview()
