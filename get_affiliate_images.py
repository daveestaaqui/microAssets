import requests
import re
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Myyco
try:
    r = requests.get("https://myyco.com", headers=headers, timeout=5)
    urls = re.findall(r'https://[^"\']*\.png', r.text) + re.findall(r'https://[^"\']*\.jpg', r.text)
    print("Myyco images:", urls[:5])
except Exception as e:
    print("Myyco error:", e)

# MagicBag
try:
    r = requests.get("https://magicbag.co", headers=headers, timeout=5)
    urls = re.findall(r'https://cdn\.shopify\.com[^"\']*\.webp', r.text) + re.findall(r'https://[^"\']*\.png', r.text)
    print("MagicBag images:", urls[:5])
except Exception as e:
    print("MagicBag error:", e)

