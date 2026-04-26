import requests
import re

URL = "https://microassets.sporlyworks.com"

def check():
    try:
        r = requests.get(URL, timeout=10)
        content = r.text
        
        print(f"Status: {r.status_code}")
        
        # Check OmniSuite logo
        if "omnisuite-logo-v2.png" in content:
            print("MATCH: OmniSuite Logo V2 is LIVE.")
        else:
            print("MISS: OmniSuite Logo V2 NOT found.")

        # Check Navigation Logo
        if "logo-nav.png" in content:
            print("MATCH: Navigation Logo is LIVE.")
            
        # Check Slogan removal in nav
        if "cultivating intelligent workflows" in content.lower() and "nav-logo" in content:
             # Check if it's INSIDE the nav-logo block
             nav_match = re.search(r'class="nav-logo".*?SporlyWorks', content, re.S)
             if nav_match and "cultivating" in nav_match.group(0).lower():
                 print("DESIGN ERROR: Slogan still in nav logo area.")
             else:
                 print("MATCH: Slogan removed from Nav (as requested).")
        
        # Check Translucency class in CSS
        # (Hard to verify live CSS via just requests, but we checked index.html)
        
        # Check Chrome Store links only
        links = re.findall(r'https://chromewebstore.google.com/detail/([a-z]+)', content)
        print(f"Total active extensions: {len(links)}")
        
    except Exception as e:
        print(f"Verify failed: {e}")

if __name__ == "__main__":
    check()
