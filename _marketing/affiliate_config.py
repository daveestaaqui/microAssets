#!/usr/bin/env python3
"""
SporlyWorks — Centralized Affiliate Program & Tracking Manager
Manages referral codes, partner tracking parameters, and outbound referral link formatting.
"""

import os
import re

# Central Affiliate Referral Codes & Tracking Parameters Configuration
AFFILIATE_CONFIG = {
    "myyco": {
        "name": "MYYCO Spore Solutions",
        "ref_param": "ref",
        "ref_code": "SporlyWorks",
        "base_domain": "myyco.com"
    },
    "magicbag": {
        "name": "Magic Bag Grow Bags",
        "ref_param": "ref",
        "ref_code": "Sporlyworks",
        "base_domain": "magicbag.co"
    },
    "nootropicsdepot": {
        "name": "Nootropics Depot (Lab-Tested Extracts)",
        "ref_param": "ref",
        "ref_code": "",  # e.g. "sporlyworks" -> appends ?ref=sporlyworks or ShareASale link
        "base_domain": "nootropicsdepot.com"
    },
    "seed": {
        "name": "Seed Health (DS-01 Daily Synbiotic)",
        "ref_param": "ref",
        "ref_code": "",  # e.g. "sporlyworks" -> appends ?ref=sporlyworks
        "base_domain": "seed.com"
    },
    "freshcap": {
        "name": "FreshCap Mushrooms",
        "ref_param": "ref",
        "ref_code": "",
        "base_domain": "freshcap.com"
    }
}

def build_affiliate_url(partner_key: str, base_url: str) -> str:
    """Formats outbound partner URL with referral parameters if configured."""
    partner = AFFILIATE_CONFIG.get(partner_key.lower())
    if not partner or not partner.get("ref_code"):
        return base_url

    ref_param = partner["ref_param"]
    ref_code = partner["ref_code"]
    
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{ref_param}={ref_code}"

if __name__ == "__main__":
    print("============================================================")
    print("  🌿 SporlyWorks Central Affiliate Link Manager")
    print("============================================================")
    for key, config in AFFILIATE_CONFIG.items():
        status = f"✅ Active ({config['ref_param']}={config['ref_code']})" if config['ref_code'] else "🟡 Live Fallback (Direct URL)"
        print(f"  • {config['name']:<40}: {status}")
    print("============================================================")
