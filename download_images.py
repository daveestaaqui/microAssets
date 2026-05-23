import requests
from bs4 import BeautifulSoup
import os

os.makedirs('assets/real_images', exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

urls = {
    "host_defense": "https://hostdefense.com/products/lions-mane-capsules",
    "freshcap": "https://freshcap.com/collections/all",
    "sporeworks": "https://sporeworks.com/Psilocybe-cubensis-Golden-Teacher-Spore-Syringe-Microscopy-Kit.html"
}

for name, url in urls.items():
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        img_url = None
        if name == "host_defense":
            img = soup.select_one('.product-single__photo img')
            if img: img_url = 'https:' + img.get('data-src', img.get('src', ''))
        elif name == "freshcap":
            img = soup.select_one('.grid-product__image')
            if img: img_url = 'https:' + img.get('data-src', img.get('src', ''))
        elif name == "sporeworks":
            img = soup.select_one('img[itemprop="image"]')
            if img: img_url = img.get('src')
            if img_url and not img_url.startswith('http'):
                img_url = 'https://sporeworks.com/' + img_url
                
        if img_url:
            print(f"Found {name}: {img_url}")
            img_data = requests.get(img_url, headers=headers).content
            with open(f"assets/real_images/{name}.png", 'wb') as f:
                f.write(img_data)
        else:
            print(f"Could not find image for {name}")
    except Exception as e:
        print(f"Error on {name}: {e}")
