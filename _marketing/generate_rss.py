#!/usr/bin/env python3
import os
import datetime
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(BASE_DIR, "blog", "articles")
OUTPUT_RSS = os.path.join(BASE_DIR, "blog", "rss.xml")

def generate_rss():
    rss = ET.Element("rss", version="2.0", attrib={"xmlns:atom": "http://www.w3.org/2005/Atom"})
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "SporlyWorks — Science-Backed Mycology & Adaptogens"
    ET.SubElement(channel, "link").text = "https://sporlyworks.com/blog/"
    ET.SubElement(channel, "description").text = "Peer-reviewed functional mushroom research, liquid culture guides, and clinical adaptogen studies."
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    atom_link = ET.SubElement(channel, "atom:link", attrib={
        "href": "https://sporlyworks.com/blog/rss.xml",
        "rel": "self",
        "type": "application/rss+xml"
    })
    
    for filename in sorted(os.listdir(ARTICLES_DIR), reverse=True):
        if filename.endswith(".md"):
            filepath = os.path.join(ARTICLES_DIR, filename)
            slug = filename[:-3]
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            title = "Mycology Research"
            summary = "Scientific research paper."
            date_str = "2026-07-11"
            
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    for line in parts[1].strip().split("\n"):
                        if ":" in line:
                            k, v = line.split(":", 1)
                            k = k.strip()
                            v = v.strip().replace('"', '')
                            if k == "title":
                                title = v
                            elif k == "summary":
                                summary = v
                            elif k == "date":
                                date_str = v

            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "link").text = f"https://sporlyworks.com/blog/{slug}.html"
            ET.SubElement(item, "guid").text = f"https://sporlyworks.com/blog/{slug}.html"
            ET.SubElement(item, "description").text = summary
            
            try:
                dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                pub_date = dt.strftime("%a, %d %b %Y 00:00:00 GMT")
            except Exception:
                pub_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
                
            ET.SubElement(item, "pubDate").text = pub_date

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    tree.write(OUTPUT_RSS, encoding="utf-8", xml_declaration=True)
    print(f"Generated RSS Feed: {OUTPUT_RSS}")

if __name__ == "__main__":
    generate_rss()
