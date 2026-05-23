import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("Fetching FreshCap from Shopify...")
# Try .jpg as well for FreshCap
r = requests.get('https://freshcap.com/products/shroom-crazy-mushroom-gummies', headers=headers)
urls = re.findall(r'https://cdn\.shopify\.com/s/files/[^"\']*\.(?:png|jpg|webp)', r.text)
for u in urls[:3]: print(u)
