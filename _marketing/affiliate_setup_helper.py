#!/usr/bin/env python3
import os
import json
import webbrowser
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "affiliate_config.json"

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print("✅ Configuration updated locally.")

def deploy_changes():
    print("\n🚀 Deploying changes to the live website...")
    try:
        # Generate updated sitemap first
        sitemap_script = BASE_DIR / "_marketing" / "generate_sitemap.py"
        if sitemap_script.exists():
            subprocess.run(["python3", str(sitemap_script)], check=True)
            
        # Git stage, commit, and push
        subprocess.run(["git", "add", "affiliate_config.json", "sitemap.xml"], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "feat: Update affiliate tracking IDs"], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
        print("🎉 Website successfully deployed and live with your affiliate links!")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

def run_wizard():
    print("=" * 70)
    print(" 🍄  SporlyWorks Interactive Affiliate Setup Wizard  🍄")
    print("=" * 70)
    print("This program will guide you through acquiring and connecting your affiliate links.")
    print("It will open the exact signup pages in Chrome, prompt you for the IDs,")
    print("and automatically write them to your site configuration and push them live.\n")
    
    config = load_config()
    partners = config.get("partners", {})
    updated = False

    # 1. FreshCap (15% Cash Commission)
    print("--- STEP 1: FreshCap (15% Cash Commission) ---")
    current_fc = partners.get("freshcap", {}).get("affiliate_id", "")
    if current_fc and not current_fc.startswith("YOUR_"):
        print(f"✅ FreshCap is already configured with ID: {current_fc}\n")
    else:
        print("We will open the FreshCap partner program application page.")
        print("After signing up and getting approved, you will receive a custom referral ID.")
        input("👉 Press Enter to open the FreshCap affiliate signup page in Chrome...")
        webbrowser.open("https://freshcap.com/pages/affiliates")
        
        while True:
            fc_id = input("\nEnter your FreshCap Affiliate ID (e.g., 'sporlyworks' or alphanumeric code) or 'skip': ").strip()
            if fc_id.lower() == 'skip':
                break
            if fc_id:
                partners["freshcap"]["affiliate_id"] = fc_id
                updated = True
                print("✅ FreshCap ID saved.")
                break
            else:
                print("❌ Invalid input. Please enter a valid ID.")
        print()

    # 2. Seed Probiotics
    print("--- STEP 2: Seed Probiotics (15% Cash Commission) ---")
    current_seed = partners.get("seed", {}).get("affiliate_id", "")
    if current_seed and not current_seed.startswith("YOUR_"):
        print(f"✅ Seed Probiotics is already configured with ID: {current_seed}\n")
    else:
        print("We will open the Seed partner application page.")
        print("Complete the partner registration and passing the 59-min SeedUniversity quiz.")
        input("👉 Press Enter to open the Seed Partner application in Chrome...")
        webbrowser.open("https://seed.com/partners")
        
        while True:
            seed_id = input("\nEnter your Seed Partner/Referral ID (e.g., 'dave15') or 'skip': ").strip()
            if seed_id.lower() == 'skip':
                break
            if seed_id:
                partners["seed"]["affiliate_id"] = seed_id
                updated = True
                print("✅ Seed Probiotics ID saved.")
                break
        print()

    # 3. North Spore (Gourmet Grow Kits)
    print("--- STEP 3: North Spore Grow Kits ($20 Store Credit per Sale) ---")
    current_ns = partners.get("north_spore", {}).get("affiliate_id", "")
    if current_ns and not current_ns.startswith("YOUR_"):
        print(f"✅ North Spore is already configured with ID: {current_ns}\n")
    else:
        print("We will open the North Spore home page. Scroll to the footer and join 'Spore Rewards' or 'Referrals'.")
        input("👉 Press Enter to open the North Spore page in Chrome...")
        webbrowser.open("https://northspore.com")
        
        while True:
            ns_id = input("\nEnter your North Spore referral ID (e.g., 'dave-mahler' or referral code) or 'skip': ").strip()
            if ns_id.lower() == 'skip':
                break
            if ns_id:
                partners["north_spore"]["affiliate_id"] = ns_id
                updated = True
                print("✅ North Spore ID saved.")
                break
        print()

    if updated:
        config["partners"] = partners
        save_config(config)
        
        deploy = input("Would you like to deploy these links live now? (y/n): ").strip().lower()
        if deploy == 'y':
            deploy_changes()
    else:
        print("No changes made to affiliate configuration.")

if __name__ == "__main__":
    run_wizard()
