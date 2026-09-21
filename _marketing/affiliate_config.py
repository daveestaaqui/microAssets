#!/usr/bin/env python3
"""
SporlyWorks — Centralized Affiliate Program & Tracking Manager
Manages referral codes, partner tracking parameters, and outbound referral link formatting.
Ensures only verified, real affiliate partnerships inject tracking parameters.
"""

import os
import re

# Central Affiliate Referral Codes & Tracking Parameters Configuration
AFFILIATE_CONFIG = {
    "myyco": {
        "name": "MYYCO Spore Solutions",
        "ref_param": "ref",
        "ref_code": "SporlyWorks",  # Verified active (UAP ID: 497)
        "base_domain": "myyco.com"
    },
    "magicbag": {
        "name": "Magic Bag Grow Bags",
        "ref_param": "ref",
        "ref_code": "Sporlyworks",  # Verified active (UAP ID: 304)
        "base_domain": "magicbag.co"
    },
    "north_spore": {
        "name": "North Spore (Gourmet Kits & Tinctures)",
        "network": "awin",
        "awin_mid": "34891",
        "ref_code": "3016315",  # Verified active Awin Publisher ID
        "base_domain": "northspore.com"
    },
    "realmushrooms": {
        "name": "Real Mushrooms (100% Organic Fruiting Body)",
        "ref_param": "ref",
        "ref_code": "",  # Unaffiliated direct fallback (Awin merchant closed, DTC pending)
        "base_domain": "realmushrooms.com"
    },
    "freshcap": {
        "name": "FreshCap Mushrooms (Organic Extracts)",
        "ref_param": "ref",
        "ref_code": "",  # Impact.com media partner account 7488636 pending review
        "base_domain": "freshcap.com"
    },
    "seed": {
        "name": "Seed Health (DS-01 Daily Synbiotic)",
        "ref_param": "ref",
        "ref_code": "",  # SeedUniversity partnership required before tracking
        "base_domain": "seed.com"
    },
    "nootropicsdepot": {
        "name": "Nootropics Depot",
        "ref_param": "ref",
        "ref_code": "",  # Direct unmonetized fallback
        "base_domain": "nootropicsdepot.com"
    }
}

def build_affiliate_url(partner_key: str, base_url: str) -> str:
    """Formats outbound partner URL with referral parameters if configured and verified."""
    partner = AFFILIATE_CONFIG.get(partner_key.lower())
    if not partner or not partner.get("ref_code"):
        return base_url

    # Check for Awin network template
    if partner.get("network") == "awin":
        mid = partner["awin_mid"]
        aid = partner["ref_code"]
        import urllib.parse
        return f"https://www.awin1.com/cread.php?awinmid={mid}&awinaffid={aid}&ued={urllib.parse.quote(base_url, safe='')}"

    ref_param = partner.get("ref_param", "ref")
    ref_code = partner["ref_code"]
    
    # If base_url already has this referral code, return as-is
    if f"{ref_param}={ref_code}" in base_url:
        return base_url

    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{ref_param}={ref_code}"

if __name__ == "__main__":
    print("============================================================")
    print("  🌿 SporlyWorks Central Affiliate Link Manager")
    print("============================================================")
    for key, config in AFFILIATE_CONFIG.items():
        status = f"✅ Active ({config.get('ref_param', 'awin')}={config['ref_code']})" if config['ref_code'] else "🟡 Live Fallback (Direct URL)"
        print(f"  • {config['name']:<40}: {status}")
    print("============================================================")
