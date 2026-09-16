"""
Unit tests for XML Feeds & Sitemap Integrity
Validates syntax, schema compliance, local file resolution, and ISO 8601 timestamps.
"""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITEMAP_PATH = ROOT / "sitemap.xml"
RSS_PATH = ROOT / "blog" / "rss.xml"
FEED_PATH = ROOT / "feed.xml"

ISO8601_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


class TestFeedsAndSitemap(unittest.TestCase):
    def test_sitemap_xml_validity(self):
        """Verify sitemap.xml exists, parses as valid XML, and points to existing files."""
        self.assertTrue(SITEMAP_PATH.is_file(), "sitemap.xml must exist")
        tree = ET.parse(SITEMAP_PATH)
        root = tree.getroot()

        self.assertIn("urlset", root.tag)
        urls = root.findall(".//{*}url")
        self.assertGreater(len(urls), 20, "Sitemap must include at least 20 pages")

        for u in urls:
            loc = u.find("{*}loc")
            self.assertIsNotNone(loc, "URL node must have loc child")
            url_text = loc.text.strip()
            self.assertTrue(url_text.startswith("https://sporlyworks.com/"))

            parsed = urlsplit(url_text)
            rel_path = unquote(parsed.path).lstrip("/")
            target = ROOT / rel_path
            self.assertTrue(
                target.is_file() or (target / "index.html").is_file(),
                f"Sitemap target does not exist locally: {url_text}"
            )

    def test_rss_xml_validity(self):
        """Verify blog/rss.xml parses as valid RSS 2.0 and has items."""
        self.assertTrue(RSS_PATH.is_file(), "blog/rss.xml must exist")
        tree = ET.parse(RSS_PATH)
        root = tree.getroot()

        self.assertEqual(root.tag, "rss")
        channel = root.find("channel")
        self.assertIsNotNone(channel, "RSS root must have a channel child")

        title = channel.find("title")
        self.assertIsNotNone(title)
        self.assertIn("SporlyWorks", title.text)

        items = channel.findall("item")
        self.assertGreater(len(items), 5, "RSS feed must contain items")

        for item in items:
            self.assertIsNotNone(item.find("title"))
            self.assertIsNotNone(item.find("link"))
            self.assertIsNotNone(item.find("description"))
            self.assertIsNotNone(item.find("pubDate"))

    def test_atom_feed_validity_and_iso8601(self):
        """Verify feed.xml parses as valid Atom and contains valid ISO 8601 timestamps."""
        self.assertTrue(FEED_PATH.is_file(), "feed.xml must exist")
        tree = ET.parse(FEED_PATH)
        root = tree.getroot()

        self.assertIn("feed", root.tag)
        feed_updated = root.find("{*}updated")
        self.assertIsNotNone(feed_updated, "Atom feed must have updated element")
        self.assertTrue(
            ISO8601_REGEX.match(feed_updated.text.strip()),
            f"Feed updated '{feed_updated.text}' must be valid ISO 8601"
        )

        entries = root.findall("{*}entry")
        self.assertGreater(len(entries), 5, "Atom feed must have entries")

        for entry in entries:
            title = entry.find("{*}title")
            published = entry.find("{*}published")
            updated = entry.find("{*}updated")

            self.assertIsNotNone(title)
            self.assertIsNotNone(published)
            self.assertIsNotNone(updated)

            self.assertTrue(
                ISO8601_REGEX.match(published.text.strip()),
                f"Entry published '{published.text}' must be valid ISO 8601"
            )
            self.assertTrue(
                ISO8601_REGEX.match(updated.text.strip()),
                f"Entry updated '{updated.text}' must be valid ISO 8601"
            )


if __name__ == "__main__":
    unittest.main()
