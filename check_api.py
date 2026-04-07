import sys, json, requests, os

TOKEN_FILE = os.path.expanduser("~/.cws_token.json")
try:
    with open(TOKEN_FILE, "r") as f:
        token = json.load(f)["access_token"]
except:
    print("Token missing")
    sys.exit()

ITEM_ID = "plnkdnnmlgjjkdnkcgaaiadaakngcjfd" 

headers = {"Authorization": f"Bearer {token}", "x-goog-api-version": "2"}
r = requests.get(f"https://www.googleapis.com/chromewebstore/v1.1/items/{ITEM_ID}?projection=PUBLISHED", headers=headers)
print("PUBLISHED Response:", r.json())
