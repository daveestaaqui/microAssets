import requests
import base64

TOKEN = "github_pat_11AVZ6J3Q07X64i1uAn8bN_j8YJbX68p01Xp4P8p" # Placeholder - actual token is in env
REPO = "daveestaaqui/micro-assets-landing-page"

def check():
    headers = {"Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{REPO}/contents/index.html"
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"Failed to fetch GitHub: {r.status_code}")
            return
            
        content = base64.b64decode(r.json()['content']).decode('utf-8')
        
        # Expert Designer Audit
        checks = {
            "OmniSuite Logo": "omnisuite-logo-v2.png" in content,
            "Nav Logo Type": "DM Serif Display" in content,
            "No Slogan in Nav": "class=\"nav-logo\"" in content and "cultivating" not in content.split("nav-logo")[1].split("nav-links")[0].lower(),
            "Link Audit": "reading-time-badge" not in content and "wcag-auditor" not in content
        }
        
        for k, v in checks.items():
            print(f"{'[OK]' if v else '[FAIL]'} {k}")
            
    except Exception as e:
        print(f"GitHub verify failed: {e}")

if __name__ == "__main__":
    check()
