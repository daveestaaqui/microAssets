#!/usr/bin/env python3
import os
import datetime
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(BASE_DIR, "blog", "articles")
OUTPUT_RSS = os.path.join(BASE_DIR, "blog", "rss.xml")
OUTPUT_ATOM = os.path.join(BASE_DIR, "feed.xml")

def generate_rss():
    # 1. Generate RSS 2.0 (blog/rss.xml)
    rss = ET.Element("rss", version="2.0", attrib={"xmlns:atom": "http://www.w3.org/2005/Atom"})
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "SporlyWorks — Science-Backed Mycology & Adaptogens"
    ET.SubElement(channel, "link").text = "https://sporlyworks.com/blog/"
    ET.SubElement(channel, "description").text = "Peer-reviewed functional mushroom research, liquid culture guides, and clinical adaptogen studies."
    ET.SubElement(channel, "language").text = "en-us"
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    ET.SubElement(channel, "lastBuildDate").text = now_utc.strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    ET.SubElement(channel, "atom:link", attrib={
        "href": "https://sporlyworks.com/blog/rss.xml",
        "rel": "self",
        "type": "application/rss+xml"
    })

    # 2. Setup Atom feed (root feed.xml) with ISO 8601 timestamps
    atom = ET.Element("feed", xmlns="http://www.w3.org/2005/Atom")
    ET.SubElement(atom, "title").text = "SporlyWorks — Scientific Mycology & Functional Adaptogens"
    ET.SubElement(atom, "subtitle").text = "Peer-reviewed functional mushroom research, cultivation protocols, and adaptogen science."
    ET.SubElement(atom, "link", href="https://sporlyworks.com/feed.xml", rel="self")
    ET.SubElement(atom, "link", href="https://sporlyworks.com/")
    ET.SubElement(atom, "id").text = "https://sporlyworks.com/"
    ET.SubElement(atom, "updated").text = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    author_elem = ET.SubElement(atom, "author")
    ET.SubElement(author_elem, "name").text = "SporlyWorks Scientific Advisory Board"
    ET.SubElement(author_elem, "uri").text = "https://sporlyworks.com"
    
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

            # Parse date
            try:
                dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
                rfc822_date = dt.strftime("%a, %d %b %Y 00:00:00 GMT")
                iso_date = dt.strftime("%Y-%m-%dT00:00:00Z")
            except Exception:
                rfc822_date = now_utc.strftime("%a, %d %b %Y %H:%M:%S GMT")
                iso_date = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Add to RSS channel
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "link").text = f"https://sporlyworks.com/blog/{slug}.html"
            ET.SubElement(item, "guid").text = f"https://sporlyworks.com/blog/{slug}.html"
            ET.SubElement(item, "description").text = summary
            ET.SubElement(item, "pubDate").text = rfc822_date

            # Add to Atom feed
            entry = ET.SubElement(atom, "entry")
            ET.SubElement(entry, "title").text = title
            ET.SubElement(entry, "link", href=f"https://sporlyworks.com/blog/{slug}.html")
            ET.SubElement(entry, "id").text = f"https://sporlyworks.com/blog/{slug}.html"
            ET.SubElement(entry, "published").text = iso_date
            ET.SubElement(entry, "updated").text = iso_date
            ET.SubElement(entry, "summary").text = summary

    # Write RSS 2.0
    rss_tree = ET.ElementTree(rss)
    ET.indent(rss_tree, space="  ")
    rss_tree.write(OUTPUT_RSS, encoding="utf-8", xml_declaration=True)
    print(f"Generated RSS Feed: {OUTPUT_RSS}")

    # Write Atom feed.xml
    atom_tree = ET.ElementTree(atom)
    ET.indent(atom_tree, space="  ")
    atom_tree.write(OUTPUT_ATOM, encoding="utf-8", xml_declaration=True)
    print(f"Generated Global Atom Feed (ISO 8601): {OUTPUT_ATOM}")

if __name__ == "__main__":
    generate_rss()
