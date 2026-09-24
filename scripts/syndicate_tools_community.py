#!/usr/bin/env python3
"""
SporlyWorks — Community & Social Tool Syndication Engine
========================================================
Generates high-value, authentic, non-spam community guides and posts
tailored for targeted subreddits (r/unclebens, r/shrooms, r/MushroomGrowers, r/mycology)
and grower forums (Shroomery, Discord channels).

Purpose:
- Accelerates time-to-first-dollar by seeding high-utility free calculators
  (Substrate Calculator, Diagnostic Wizard, Yield Estimator) directly to
  high-intent cultivators and enthusiasts.
- Each post provides 100% standalone value (formulas, ratios, diagnostic cues)
  with the SporlyWorks tools linked as free open web calculators.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "marketing" / "community_posts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMMUNITY_TEMPLATES = [
    {
        "platform": "reddit",
        "target_community": "r/unclebens",
        "topic": "Substrate & Hydration Calculator for Shoeboxes",
        "title": "[Guide + Tool] Coir Field Capacity & Spawn-to-Bulk Ratio Calculator (No more guessing grams of boiling water)",
        "body": """Hey everyone,

One of the most common issues for beginners transitioning from colonized grain bags to fruiting tubs is getting coir field capacity wrong (either too soupy causing bacterial wet rot, or too dry stalling the first flush).

Here is the exact baseline formula for a standard 6-quart shoebox:

### Standard 1:1 to 1:2 CVG Formula (Per 650g Brick of Coco Coir):
- **Coco Coir:** 650 grams
- **Vermiculite:** 2 quarts (~8 cups, coarse horticultural)
- **Gypsum:** 1 cup (calcium sulfate)
- **Boiling Water:** 3.25 to 3.5 quarts (13 to 14 cups)

### The Squeeze Test Benchmark:
When you grab a handful of pasteurized substrate:
- When gently compressed: only 2–3 drops of water should seep between your fingers.
- If water streams out: it's over-saturated.
- If no moisture beads at all: mist or add sterilized water.

To make this seamless without manual math across different tub sizes (6qt shoebox, 32qt monotub, 66qt tote), I built a free, zero-ad interactive calculator:
👉 **https://sporlyworks.com/tools/substrate-calculator.html**

You just punch in your target tub volume or coir brick weight, and it outputs the exact hydration water volume, vermiculite cups, and gypsum tablespoons instantly.

Hope this helps save some tubs this week! Drop any tub dimensions in the comments if you want the custom ratio checked.
"""
    },
    {
        "platform": "reddit",
        "target_community": "r/shrooms",
        "topic": "Trichoderma vs. Bruising Contamination Diagnosis",
        "title": "[Visual Diagnostic Protocol] How to tell if that green/blue spot is Trichoderma or just Mycelium Bruising (The Q-Tip Test + Cues)",
        "body": """Every grower eventually faces the dreaded morning panicking over a discolored patch in their fruiting tub. Here is the field-tested diagnostic protocol to know for sure within 30 seconds before tossing a tub:

### 1. The Sterile Q-Tip Test (Fastest Confirmation)
Take a clean cotton swab and gently swab the suspect area:
- **If the cotton comes away clean white:** It is **mycelial bruising** (oxidation of secondary metabolites).
- **If pigment or green/grey powder transfers to the cotton:** It is **sporulating mold spores (Trichoderma harzianum or Penicillium)**.

### 2. Texture & Morphology Differences
- **Bruising:** Smooth, flat surface following the exact contour of the mycelium. Appears deep sky-blue to slate-teal. Often caused by direct heavy misting, dry airflow from a fan, or physical disturbance.
- **Trichoderma:** Starts as an unusually bright, dense, chalky white patch that looks like thick cotton candy (far denser than healthy tomentose mycelium). Within 24–48 hours, it turns powdery forest green from center outward as it sporulates.

### 3. Immediate Action Plan
- If it's bruising: back off direct misting, maintain high relative humidity (90–95%), and leave the lid latched.
- If it's Trichoderma: seal the tub immediately, remove it from your grow space, and dispose of it outdoors to avoid contaminating your cleanroom.

For more diagnostic cues covering cobweb mold, wet bubble (Mycogone), bacterial blotch, and fuzzy feet:
👉 **https://sporlyworks.com/tools/diagnostics.html**

The tool lets you click your exact visual symptom, smell, and growth speed to get an instant remediation protocol.

Happy harvesting!
"""
    },
    {
        "platform": "reddit",
        "target_community": "r/MushroomGrowers",
        "topic": "Biological Efficiency & First Flush Yield Projections",
        "title": "[Resource] Biological Efficiency (B.E.) Calculation & Flush Projection Tool for Gourmet & Active Strains",
        "body": """Quick discussion on realistic yield modeling across different grain-to-bulk ratios and species.

### What is Biological Efficiency (B.E.)?
Biological Efficiency measures the conversion efficiency of dry substrate mass into fresh harvested mushrooms:
`B.E. (%) = (Total Fresh Weight Harvested / Total Dry Weight of Substrate) * 100`

### Expected Benchmarks by Species:
1. **Oyster Mushrooms (Pleurotus ostreatus):** 75% to 150% B.E. (exceptionally aggressive lignocellulose digesters on pasteurized straw/hardwood).
2. **Lion’s Mane (Hericium erinaceus):** 70% to 100% B.E. on master's mix (50/50 hardwood sawdust & soy hulls).
3. **Psilocybe cubensis:** 100% B.E. benchmark on CVG (typically yields 1 oz dry / ~280g fresh per quart of colonized grain spawn across 3 flushes).

If you want to estimate your expected yield from your current grain spawn volume or compare expected flushes:
👉 **https://sporlyworks.com/tools/yield-estimator.html**

It accounts for strain lineage, flush number degradation curves, and grain weight ratios.
"""
    }
]


def run_syndication():
    generated_manifest = []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    for i, item in enumerate(COMMUNITY_TEMPLATES, 1):
        filename = f"{item['target_community'].replace('/', '_')}_{i}_{timestamp}.md"
        filepath = OUTPUT_DIR / filename

        content = f"""# {item['title']}
**Platform:** {item['platform']} | **Target:** {item['target_community']}  
**Topic:** {item['topic']}  
**Generated:** {datetime.now(timezone.utc).isoformat()}  

---

{item['body']}

---
*Generated by SporlyWorks Community Syndication Engine.*
"""
        filepath.write_text(content, encoding="utf-8")
        generated_manifest.append({
            "target": item["target_community"],
            "title": item["title"],
            "file": str(filepath.relative_to(ROOT))
        })
        print(f"✓ Generated high-yield community draft for {item['target_community']}: {filename}")

    # Save manifest
    manifest_path = OUTPUT_DIR / "syndication_manifest.json"
    manifest_path.write_text(json.dumps(generated_manifest, indent=2), encoding="utf-8")
    print(f"\nSaved {len(generated_manifest)} community syndication drafts to {OUTPUT_DIR}")


if __name__ == "__main__":
    run_syndication()
