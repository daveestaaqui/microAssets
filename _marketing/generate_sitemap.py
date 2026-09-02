#!/usr/bin/env python3
import os
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = "https://sporlyworks.com"

def get_lastmod(filepath):
    mtime = os.path.getmtime(filepath)
    return datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

def is_excluded(filepath):
    name = filepath.name.lower()
    return any(x in name for x in ['dummy', 'test', 'dashboard'])

def add_url(xml_content, url_path, priority, filepath):
    if is_excluded(filepath):
        return
    lastmod = get_lastmod(filepath)
    xml_content.append(f"  <url>\n    <loc>{BASE_URL}/{url_path}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <priority>{priority}</priority>\n  </url>")

def generate_sitemap():
    print("=" * 60)
    print("  🗺️ Generating Auto-Scanning Mycology XML Sitemap")
    print("=" * 60)
    
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Root files
    add_url(xml_content, "index.html", "1.0", BASE_DIR / "index.html")
    add_url(xml_content, "products.html", "0.9", BASE_DIR / "products.html")
    
    # Products
    products_dir = BASE_DIR / "products"
    if products_dir.exists():
        for f in products_dir.glob("*.html"):
            add_url(xml_content, f"products/{f.name}", "0.8", f)
            
    # Tools
    tools_dir = BASE_DIR / "tools"
    if tools_dir.exists():
        for f in tools_dir.glob("*.html"):
            add_url(xml_content, f"tools/{f.name}", "0.8", f)
            
    # Blog
    blog_dir = BASE_DIR / "blog"
    if blog_dir.exists():
        add_url(xml_content, "blog/index.html", "0.7", blog_dir / "index.html")
        add_url(xml_content, "blog/rss.xml", "0.7", blog_dir / "rss.xml")
        for f in blog_dir.glob("*.html"):
            if f.name != "index.html":
                add_url(xml_content, f"blog/{f.name}", "0.6", f)

    # Guides (Programmatic SEO)
    guides_dir = BASE_DIR / "guides"
    if guides_dir.exists():
        for f in guides_dir.glob("*.html"):
            add_url(xml_content, f"guides/{f.name}", "0.75", f)
                
    xml_content.append("</urlset>")
    
    sitemap_path = BASE_DIR / "sitemap.xml"
    with open(sitemap_path, 'w') as f:
        f.write("\n".join(xml_content))
        
    print(f"✅ Sitemap successfully generated at {sitemap_path}")

if __name__ == "__main__":
    generate_sitemap()
