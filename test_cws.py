import requests, re

url = "https://chromewebstore.google.com/detail/fkjkpijpiecandcaehphllpjiehofmad"
r = requests.get(url)
print(f"Status: {r.status_code}")
v = re.search(r'"version":"([0-9\.]+)"', r.text)
if v:
    print(f"Version: {v.group(1)}")
else:
    print("Version not found")
