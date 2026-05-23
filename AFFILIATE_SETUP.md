# SporlyWorks Affiliate Setup Guide

## Quick Start

1. Sign up for each affiliate program below
2. Get your unique affiliate/referral ID from each dashboard
3. Update `affiliate_config.json` — replace each `YOUR_XXX_ID` with your real ID
4. Push to GitHub Pages — all links auto-populate from the config

---

## Partner Programs

### 1. MYYCO — Premium Liquid Cultures
- **Apply**: Visit [myyco.com](https://www.myyco.com) → Footer → "Affiliate Program"
- **Commission**: Typically 10-15% per sale
- **Cookie**: 30 days
- **Config key**: `myyco` → `affiliate_id`

### 2. Magic Bag — All-In-One Grow Bags
- **Apply**: Visit [magicbag.co](https://www.magicbag.co) → "Partners" or email their team
- **Commission**: Typically 10% per sale
- **Cookie**: 30 days
- **Config key**: `magicbag` → `affiliate_id`

### 3. Real Mushrooms — Organic Extracts
- **Apply**: [realmushrooms.com/affiliate-program](https://www.realmushrooms.com/affiliate-program/) or via ShareASale
- **Commission**: 15-25% per sale
- **Cookie**: 90 days
- **Config key**: `real_mushrooms` → `affiliate_id`

### 4. Seed Probiotics — DS-01® Daily Synbiotic
- **Apply**: [seed.com/refer](https://seed.com/refer) or email partnerships@seed.com
- **Commission**: $10-20 per referral
- **Cookie**: 30 days
- **Config key**: `seed` → `affiliate_id`

---

## How It Works

The site loads `affiliate_config.json` at page load and dynamically populates all CTA buttons with your affiliate URLs. This means:

- **Zero hardcoded links** — change one JSON file, all links update
- **Easy A/B testing** — swap affiliate IDs instantly
- **New partners** — just add a new entry to the JSON config

## Legal Requirements

All affiliate links are disclosed via the footer disclaimer. Ensure your site always includes:
- FTC affiliate disclosure
- FDA supplement disclaimer
- Local cultivation law notice
