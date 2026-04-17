#!/usr/bin/env python3
"""
Portfolio Pruning Analyzer
==========================
Identifies extensions that should be sunset to reduce maintenance burden,
QA surface area, and brand risk from broken/low-quality products.

Scoring criteria (lower = more cuttable):
  - Market differentiation (commodity tools score low)
  - Maintenance risk (complex permissions, background scripts = higher risk)
  - Revenue potential (no Pro path = dead weight)
  - Portfolio overlap (redundant tools cannibalize each other)

Usage:
    python3 portfolio_pruner.py              # Analyze and recommend cuts
    python3 portfolio_pruner.py --tier       # Show full tier breakdown
"""

import os
import json
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

# ── Overlap Groups ───────────────────────────────────────────────────────
# Extensions that overlap functionally. Only the strongest in each group
# should survive. The rest are dead weight that confuse users and dilute brand.

OVERLAP_GROUPS = {
    "json_tools": ["json-formatter", "json-csv-converter", "json-path-finder"],
    "diff_tools": ["diff-viewer", "diff-checker"],
    "css_generators": ["css-gradient-generator", "css-flexbox-generator", "css-grid-generator", "css-box-shadow"],
    "note_tools": ["quick-notepad", "quick-note-taker"],
    "http_debug": ["http-headers", "http-status-checker"],
    "seo_tools": ["page-seo-analyzer", "seo-content-pro", "og-previewer", "meta-tag-editor", "robots-viewer"],
    "cookie_tools": ["cookie-manager", "cookie-banner-rejector"],
    "network_tools": ["network-speed-test", "network-monitor-pro", "website-monitor-pro", "site-speed-analyzer"],
}

# Best-in-class per group (keep these, consider cutting the rest)
GROUP_WINNERS = {
    "json_tools": "json-formatter",
    "diff_tools": "diff-checker",
    "css_generators": "css-inspector-pro",  # Supersedes individual generators
    "note_tools": "quick-note-taker",
    "http_debug": "http-headers",
    "seo_tools": "seo-content-pro",
    "cookie_tools": "cookie-manager",
    "network_tools": "network-monitor-pro",
}

# Extensions with near-zero differentiation (hundreds of alternatives exist)
COMMODITY_EXTENSIONS = {
    "qr-code-generator",        # Saturated market, zero moat
    "password-generator",       # Built into every browser
    "screenshot-capture",       # Built into Chrome/Firefox
    "lorem-ipsum-generator",    # Trivial utility, no WTP
    "hash-generator",           # Dev commodity
    "base64-encoder",           # Dev commodity
    "url-encoder-decoder",      # Dev commodity
    "word-counter",             # Extremely basic
    "text-case-converter",      # Extremely basic
    "timestamp-converter",      # Extremely basic
    "reading-time-badge",       # Very niche, no revenue path
    "dark-mode-everywhere",     # Hundreds of competitors
    "reading-mode",             # Built into browsers
    "clipboard-history",        # OS-level solutions exist
    "bookmark-manager",         # Built into browsers
    "url-shortener",            # Free web services dominate
    "carbon-footprint-checker", # Novelty, no retention
    "google-dark-search",       # Niche cosmetic
    "amazon-wide-mode",         # Single-site cosmetic
}

# High-value keepers (never suggest cutting)
FLAGSHIP_EXTENSIONS = {
    "api-tester-pro", "css-inspector-pro", "network-monitor-pro",
    "seo-content-pro", "site-speed-analyzer", "dom-editor-pro",
    "privacy-scanner", "wcag-auditor", "ai-content-bouncer",
    "llm-privacy-scrub", "contract-highlighter", "omnisuite-master-suite",
    "form-filler-pro", "crm-data-extractor", "invoice-extractor",
    "amazon-fake-review-skimmer",
}


def analyze_extension(name, manifest_path):
    """Score an extension's keep-worthiness (0-100, higher = keep)."""
    score = 50  # Base score

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except Exception:
        return score, ["BROKEN_MANIFEST"]

    flags = []

    # Flagship bonus
    if name in FLAGSHIP_EXTENSIONS:
        score += 40
        flags.append("FLAGSHIP")

    # Commodity penalty
    if name in COMMODITY_EXTENSIONS:
        score -= 30
        flags.append("COMMODITY")

    # Overlap penalty
    for group_name, members in OVERLAP_GROUPS.items():
        if name in members:
            winner = GROUP_WINNERS.get(group_name)
            if winner and name != winner:
                score -= 15
                flags.append(f"OVERLAPS:{winner}")

    # "Pro" in name bonus (signals monetizable positioning)
    if "pro" in name.lower():
        score += 10
        flags.append("PRO_TIER")

    # Complexity risk: more permissions = more things that can break
    perms = manifest.get("permissions", [])
    if len(perms) > 5:
        score -= 5
        flags.append(f"HIGH_PERMS:{len(perms)}")

    # Background script risk (more likely to break silently)
    if manifest.get("background", {}).get("service_worker") or manifest.get("background", {}).get("scripts"):
        score -= 3
        flags.append("BG_SCRIPT")

    # Content script risk (can break on target site changes)
    content_scripts = manifest.get("content_scripts", [])
    if content_scripts:
        total_matches = sum(len(cs.get("matches", [])) for cs in content_scripts)
        if total_matches > 3:
            score -= 5
            flags.append(f"WIDE_INJECT:{total_matches}")

    return max(0, min(100, score)), flags


def run_analysis():
    """Analyze the full portfolio and output tier recommendations."""
    results = []

    for item in sorted(os.listdir(REPO_ROOT)):
        item_path = os.path.join(REPO_ROOT, item)
        if not os.path.isdir(item_path) or item.startswith(("_", ".")):
            continue
        if "-firefox" in item:
            continue  # Firefox variants follow Chrome decisions
        manifest_path = os.path.join(item_path, "manifest.json")
        if not os.path.isfile(manifest_path):
            continue

        score, flags = analyze_extension(item, manifest_path)
        results.append({
            "name": item,
            "score": score,
            "flags": flags,
        })

    results.sort(key=lambda x: x["score"])

    # Tier assignments
    cut_candidates = [r for r in results if r["score"] < 30]
    review_tier = [r for r in results if 30 <= r["score"] < 50]
    keep_tier = [r for r in results if 50 <= r["score"] < 75]
    flagship_tier = [r for r in results if r["score"] >= 75]

    print("=" * 75)
    print("PORTFOLIO PRUNING ANALYSIS")
    print(f"Total Chrome extensions analyzed: {len(results)}")
    print("=" * 75)

    print(f"\n🔴 RECOMMENDED CUT ({len(cut_candidates)} extensions)")
    print("   These generate no revenue, have hundreds of free alternatives,")
    print("   and each one is a surface for broken UX that damages the brand.")
    print("-" * 75)
    for r in cut_candidates:
        print(f"  {r['score']:3d}  {r['name']:<40} {', '.join(r['flags'])}")

    print(f"\n🟡 REVIEW ({len(review_tier)} extensions)")
    print("   These have marginal value. Consider consolidation or bundling.")
    print("-" * 75)
    for r in review_tier:
        print(f"  {r['score']:3d}  {r['name']:<40} {', '.join(r['flags'])}")

    print(f"\n🟢 KEEP ({len(keep_tier)} extensions)")
    print("-" * 75)
    for r in keep_tier:
        print(f"  {r['score']:3d}  {r['name']:<40} {', '.join(r['flags'])}")

    print(f"\n⭐ FLAGSHIP ({len(flagship_tier)} extensions)")
    print("   These are the revenue core. Focus ALL monetization here.")
    print("-" * 75)
    for r in flagship_tier:
        print(f"  {r['score']:3d}  {r['name']:<40} {', '.join(r['flags'])}")

    # Summary
    print("\n" + "=" * 75)
    print("EXECUTIVE SUMMARY")
    print("=" * 75)
    print(f"  Cut:      {len(cut_candidates):3d} extensions (saves ~{len(cut_candidates)*2} QA checks/cycle)")
    print(f"  Review:   {len(review_tier):3d} extensions")
    print(f"  Keep:     {len(keep_tier):3d} extensions")
    print(f"  Flagship: {len(flagship_tier):3d} extensions")
    print(f"  Firefox variants saved by cuts: ~{len(cut_candidates)} (1:1 ratio)")
    print(f"  Total surface area reduction: ~{len(cut_candidates) * 2} products")
    print()
    if cut_candidates:
        cut_names = [r["name"] for r in cut_candidates]
        print(f"  If you cut all {len(cut_candidates)} recommendations:")
        print(f"    Portfolio: {len(results)} → {len(results) - len(cut_candidates)} Chrome extensions")
        print(f"    With Firefox: {len(results)*2} → {(len(results) - len(cut_candidates))*2} total")
        print(f"    QA checks eliminated: ~{len(cut_candidates) * 10} per daemon cycle")

    # Write machine-readable report
    report = {
        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "total_analyzed": len(results),
        "cut_candidates": [r["name"] for r in cut_candidates],
        "review_tier": [r["name"] for r in review_tier],
        "keep_tier": [r["name"] for r in keep_tier],
        "flagship_tier": [r["name"] for r in flagship_tier],
        "full_scores": results,
    }
    report_path = os.path.join(REPO_ROOT, "marketing", "portfolio_pruning_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Full report saved to: marketing/portfolio_pruning_report.json")


if __name__ == "__main__":
    run_analysis()
