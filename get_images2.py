import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
}

print("Fetching Premium Spores...")
r = requests.get('https://premiumspores.com/product/b-mushroom-spore-syringe-print/', headers=headers)
urls = re.findall(r'https://premiumspores\.com/wp-content/uploads/[^"\']*\.jpg', r.text)
for u in urls[:3]: print(u)
