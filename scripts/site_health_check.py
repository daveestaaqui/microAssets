"""
SporlyWorks — Automated Site Health & Institutional Link Verification Suite
Modeled after the Surplus Docket health check architecture.
Dependency-free: parses every public HTML page, asserts canonical URLs,
validates internal links, verifies OG/Twitter meta tags, checks schema.org JSON-LD,
and validates sitemap.xml against robots.txt.
"""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://sporlyworks.com"

# Excluded folders / patterns that are non-site or internal developer tools
EXCLUDE_DIRS = {
    "_marketing", "b2b-marketing-hub", "microassets-chrome-hub",
    "omnisuite_platform", "_landing_page", "CWS_Upload_Ready",
    "_installer", "_infrastructure", "_license_server", "_social_engine",
    "_worker", "_workers", "localtunnel-bypasser", "scratch", "tests",
    "gh_2.58.0_macOS_arm64", "~", ".git", ".github",
    "marketing", "sporelyworks"
}

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.canonical = None
        self.og_tags = {}
        self.twitter_tags = {}
        self.json_ld_scripts = []
        self._in_json_ld = False
        self._json_ld_buffer = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Collect links and sources
        for key in ("href", "src"):
            val = attrs_dict.get(key)
            if val and not val.startswith(("mailto:", "tel:", "javascript:", "#")):
                # Strip query and fragments for target checking
                self.links.append(val)

        # Canonical tag
        if tag == "link" and attrs_dict.get("rel") == "canonical":
            self.canonical = attrs_dict.get("href")

        # OpenGraph and Twitter meta tags
        if tag == "meta":
            prop = attrs_dict.get("property") or attrs_dict.get("name")
            content = attrs_dict.get("content")
            if prop and content:
                if prop.startswith("og:"):
                    self.og_tags[prop] = content
                elif prop.startswith("twitter:"):
                    self.twitter_tags[prop] = content

        # JSON-LD script
        if tag == "script" and attrs_dict.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_buffer = []

    def handle_data(self, data):
        if self._in_json_ld:
            self._json_ld_buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_json_ld:
            self._in_json_ld = False
            raw = "".join(self._json_ld_buffer).strip()
            if raw:
                self.json_ld_scripts.append(raw)


def is_site_page(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return False
    # Exclude internal dashboards or temp files
    name = path.name
    if name.startswith("Design_Review_Dashboard") or name.startswith("dummy_popup"):
        return False
    return True


def target_exists(base_page: Path, raw_url: str) -> bool:
    parsed = urlsplit(raw_url)
    clean_path = unquote(parsed.path)

    if parsed.netloc and parsed.netloc not in ("sporlyworks.com", "www.sporlyworks.com"):
        # External URL, skipped in local offline existence check
        return True

    if clean_path.startswith("/"):
        target = ROOT / clean_path.lstrip("/")
    else:
        target = (base_page.parent / clean_path).resolve()

    # Allow query parameter cache busting
    if target.is_dir():
        return (target / "index.html").is_file()
    if target.is_file():
        return True
    if not target.suffix and target.with_suffix(".html").is_file():
        return True

    return False


def check(live=False):
    errors = []
    checked_pages = 0
    
    # Discover all relevant HTML pages
    all_pages = [p for p in ROOT.rglob("*.html") if is_site_page(p)]
    
    for page in sorted(all_pages):
        checked_pages += 1
        rel_page = page.relative_to(ROOT).as_posix()
        html_text = page.read_text(encoding="utf-8", errors="replace")
        
        parser = PageParser()
        parser.feed(html_text)

        # 1. Verify internal links
        for link in parser.links:
            parsed = urlsplit(link)
            # Internal link check
            if not parsed.netloc or parsed.netloc in ("sporlyworks.com", "www.sporlyworks.com"):
                if not target_exists(page, link):
                    errors.append(f"{rel_page}: broken internal link -> {link}")

        # 2. Canonical URL validation
        # embed pages are iframe widgets; welcome is post-checkout. Main pages should have canonical.
        is_embed = "embed/" in rel_page
        if not parser.canonical and not is_embed:
            errors.append(f"{rel_page}: missing canonical link tag")
        elif parser.canonical:
            if not parser.canonical.startswith("https://sporlyworks.com"):
                errors.append(f"{rel_page}: canonical URL must start with https://sporlyworks.com (found: {parser.canonical})")

        # 3. OpenGraph / Twitter tags check (for primary pages)
        is_primary = not is_embed and rel_page != "welcome.html"
        if is_primary:
            for required_og in ("og:title", "og:description"):
                if required_og not in parser.og_tags:
                    errors.append(f"{rel_page}: missing {required_og} meta tag")

        # 4. JSON-LD scripts validation
        for raw_json in parser.json_ld_scripts:
            try:
                parsed_json = json.loads(raw_json)
                items = parsed_json if isinstance(parsed_json, list) else [parsed_json]
                for item in items:
                    if not isinstance(item, dict):
                        errors.append(f"{rel_page}: schema.org JSON-LD root must be an object")
                        continue
                    if "@context" not in item:
                        errors.append(f"{rel_page}: schema.org JSON-LD missing @context")
                    if "@graph" in item and isinstance(item["@graph"], list):
                        for sub_idx, sub in enumerate(item["@graph"]):
                            if not isinstance(sub, dict) or "@type" not in sub:
                                errors.append(f"{rel_page}: schema.org JSON-LD @graph[{sub_idx}] missing @type")
                    elif "@type" not in item:
                        errors.append(f"{rel_page}: schema.org JSON-LD missing @type")
            except json.JSONDecodeError as e:
                errors.append(f"{rel_page}: invalid schema.org JSON-LD: {e}")

    # 5. Sitemap check
    sitemap_path = ROOT / "sitemap.xml"
    if not sitemap_path.is_file():
        errors.append("sitemap.xml not found")
    else:
        try:
            tree = ET.parse(sitemap_path)
            urls = [node.text.strip() for node in tree.findall(".//{*}loc") if node.text]
            for url in urls:
                parsed = urlsplit(url)
                if parsed.netloc != "sporlyworks.com":
                    errors.append(f"sitemap.xml contains invalid host: {url}")
                path_part = unquote(parsed.path).lstrip("/")
                target = ROOT / path_part
                if not target.is_file() and not (target / "index.html").is_file():
                    errors.append(f"sitemap.xml target does not exist locally: {url}")
        except Exception as e:
            errors.append(f"sitemap.xml parse error: {e}")

    # 6. Robots.txt check
    robots_path = ROOT / "robots.txt"
    if not robots_path.is_file():
        errors.append("robots.txt not found")
    else:
        robots_text = robots_path.read_text(encoding="utf-8")
        if f"{ORIGIN}/sitemap.xml" not in robots_text:
            errors.append("robots.txt does not advertise https://sporlyworks.com/sitemap.xml")

    # 7. Optional live checks
    live_results = {}
    if live:
        for path in ("/", "/robots.txt", "/sitemap.xml"):
            try:
                req = Request(f"{ORIGIN}{path}", headers={"User-Agent": "SporlyWorks-HealthCheck/1.0"})
                with urlopen(req, timeout=20) as resp:
                    live_results[path] = resp.status
            except Exception as e:
                errors.append(f"Live check failed for {path}: {e}")

    report = {
        "html_pages_checked": checked_pages,
        "live_get_checks": live_results,
        "errors": sorted(set(errors)),
        "ok": len(errors) == 0
    }
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SporlyWorks Site Health Check")
    parser.add_argument("--live", action="store_true", help="Perform live HTTP checks")
    args = parser.parse_args()

    result = check(live=args.live)
    output_path = ROOT / "site-health.json"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)
