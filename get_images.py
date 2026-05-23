import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
}

print("Fetching FreshCap...")
r = requests.get('https://freshcap.com/products/shroom-crazy-mushroom-gummies', headers=headers)
urls = re.findall(r'https://cdn\.shopify\.com/s/files/[^"\']*\.png', r.text)
for u in urls[:3]: print(u)

print("Fetching SporeWorks...")
r = requests.get('https://sporeworks.com/Psilocybe-cubensis-Golden-Teacher-Spore-Syringe-Microscopy-Kit.html', headers=headers)
urls = re.findall(r'https?://sporeworks\.com/images/[^"\']*\.jpg', r.text)
if not urls:
    urls = re.findall(r'images/[^"\']*\.jpg', r.text)
for u in urls[:3]: print(u)
