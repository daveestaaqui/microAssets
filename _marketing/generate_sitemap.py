#!/usr/bin/env python3
import os
from pathlib import Path
import datetime

BASE_DIR = Path("/Users/davidmahler/Desktop/microAssets")
BASE_URL = "https://sporlyworks.com"

def generate_sitemap():
    print("=" * 60)
    # Generate XML Sitemap for sporlyworks.com mycology affiliate site
    print("  🗺️ Generating Mycology & Wellness XML Sitemap")
    print("=" * 60)
    
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # 1. Add Index Hub (1.0 priority)
    xml_content.append(f"  <url>\n    <loc>{BASE_URL}/index.html</loc>\n    <lastmod>{today}</lastmod>\n    <priority>1.0</priority>\n  </url>")
    
    # 2. Add root static pages (privacy, terms, etc.)
    for f in os.listdir(BASE_DIR):
        if f.endswith(".html") and f != "index.html":
            # Determine priority
            prio = "0.7"
            if f in ["privacy.html", "terms.html"]:
                prio = "0.3"
            xml_content.append(f"  <url>\n    <loc>{BASE_URL}/{f}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>{prio}</priority>\n  </url>")
            
    # 3. Add guides from the guides/ folder
    guides_dir = BASE_DIR / "guides"
    if guides_dir.exists():
        for f in os.listdir(guides_dir):
            if f.endswith(".html"):
                xml_content.append(f"  <url>\n    <loc>{BASE_URL}/guides/{f}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.9</priority>\n  </url>")
                
    # 4. Add products from the products/ folder
    products_dir = BASE_DIR / "products"
    if products_dir.exists():
        for f in os.listdir(products_dir):
            if f.endswith(".html"):
                xml_content.append(f"  <url>\n    <loc>{BASE_URL}/products/{f}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.9</priority>\n  </url>")
                
    xml_content.append("</urlset>")
    
    sitemap_path = BASE_DIR / "sitemap.xml"
    with open(sitemap_path, 'w') as f:
        f.write("\n".join(xml_content))
        
    print(f"✅ Sitemap successfully generated at {sitemap_path}")

if __name__ == "__main__":
    generate_sitemap()
