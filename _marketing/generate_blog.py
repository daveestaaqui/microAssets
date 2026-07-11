#!/usr/bin/env python3
import os
import re
import datetime

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
ARTICLES_DIR = os.path.join(BASE_DIR, "blog", "articles")
OUTPUT_DIR = os.path.join(BASE_DIR, "blog")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cache-busting stylesheet parameter
STYLE_PATH = "../style.css?v=700"
FAVICON_PATH = "../assets/favicon.ico"
NAV_ICON = "../assets/logo-nav.png"

# Basic Markdown-to-HTML parser (Zero-dependency)
def parse_markdown(md_text):
    html = ""
    lines = md_text.strip().split("\n")
    in_list = False
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Handle Code Blocks
        if stripped.startswith("```"):
            if in_code_block:
                html += "</code></pre>\n"
                in_code_block = False
            else:
                html += "<pre><code>"
                in_code_block = True
            continue

        if in_code_block:
            # Escape HTML characters in code block
            escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html += escaped + "\n"
            continue

        # Handle Lists
        if stripped.startswith("* ") or stripped.startswith("- "):
            if not in_list:
                html += "<ul>\n"
                in_list = True
            item_text = stripped[2:]
            html += f"  <li>{parse_inline(item_text)}</li>\n"
            continue
        else:
            if in_list:
                html += "</ul>\n"
                in_list = False

        # Handle Headers
        if stripped.startswith("### "):
            html += f"<h3>{parse_inline(stripped[4:])}</h3>\n"
        elif stripped.startswith("## "):
            html += f"<h2>{parse_inline(stripped[3:])}</h2>\n"
        elif stripped.startswith("# "):
            html += f"<h1>{parse_inline(stripped[2:])}</h1>\n"
        # Handle Blockquotes
        elif stripped.startswith("> "):
            html += f"<blockquote class=\"blog-quote\">{parse_inline(stripped[2:])}</blockquote>\n"
        # Horizontal Rules
        elif stripped == "---":
            html += "<hr class=\"blog-divider\">\n"
        # Empty Line
        elif not stripped:
            html += "\n"
        # Regular Paragraph
        else:
            html += f"<p>{parse_inline(line)}</p>\n"

    if in_list:
        html += "</ul>\n"

    # Post-processing: wrap multi-line text into paragraph groups nicely
    html = re.sub(r'<p>(.*?)</p>\n<p>(.*?)</p>', r'<p>\1 \2</p>', html)
    # Clean up empty paragraphs
    html = html.replace("<p></p>", "")
    return html

def parse_inline(text):
    # Escape simple HTML brackets to prevent broken layouts
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    # Bold: **text** -> <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic: *text* -> <em>text</em>
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Inline code: `code` -> <code>code</code>
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text

# Template for individual blog article page
ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — SporlyWorks Science-Backed Blog</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <link rel="canonical" href="https://sporlyworks.com/blog/{slug}.html">
    <link rel="icon" type="image/x-icon" href="{favicon}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{style_path}">
    <style>
        .blog-container {{
            max-width: 800px;
            margin: 140px auto 80px;
            padding: 0 24px;
        }}
        .blog-header-section {{
            margin-bottom: 40px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 24px;
        }}
        .blog-title {{
            font-family: 'Cinzel', serif;
            font-size: 36px;
            color: var(--green-dark);
            margin-bottom: 16px;
            line-height: 1.3;
        }}
        .blog-meta {{
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            color: var(--text-muted);
            display: flex;
            gap: 20px;
        }}
        .blog-author {{
            font-weight: 600;
            color: var(--green-dark);
        }}
        .blog-body {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 20px;
            line-height: 1.7;
            color: var(--text-dark);
        }}
        .blog-body p {{
            margin-bottom: 24px;
        }}
        .blog-body h2 {{
            font-family: 'Cinzel', serif;
            font-size: 24px;
            color: var(--green-dark);
            margin: 40px 0 20px;
        }}
        .blog-body h3 {{
            font-family: 'Cinzel', serif;
            font-size: 20px;
            color: var(--green-dark);
            margin: 32px 0 16px;
        }}
        .blog-quote {{
            font-style: italic;
            border-left: 4px solid var(--gold-light);
            padding-left: 20px;
            margin: 32px 0;
            color: var(--text-muted);
        }}
        .blog-divider {{
            border: 0;
            height: 1px;
            background: var(--border-color);
            margin: 40px 0;
        }}
        .blog-footer-cta {{
            background: rgba(245, 240, 232, 0.4);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 32px;
            margin-top: 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 20px;
        }}
        .blog-footer-cta h4 {{
            font-family: 'Cinzel', serif;
            font-size: 18px;
            color: var(--green-dark);
            margin-bottom: 8px;
        }}
        .blog-footer-cta p {{
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            color: var(--text-muted);
            max-width: 500px;
            margin-bottom: 0;
        }}
        .btn-blog-cta {{
            background: var(--green-dark);
            color: var(--text-on-dark);
            padding: 12px 24px;
            border-radius: var(--radius-sm);
            font-family: 'Cinzel', serif;
            font-size: 13px;
            font-weight: 700;
            text-decoration: none;
            transition: all 0.3s ease;
        }}
        .btn-blog-cta:hover {{
            background: #1e3527;
            transform: translateY(-2px);
        }}
    </style>
</head>
<body>

    <!-- ═══ NAVIGATION ═══ -->
    <nav id="mainNav" class="scrolled">
        <div class="nav-inner">
            <a href="../index.html" class="nav-brand">
                <img src="../assets/icon-128.png" alt="SporlyWorks" class="nav-icon">
                <span class="nav-wordmark" style="font-size:24px;">SPORLYWORKS</span>
            </a>
            <div class="nav-links">
                <a href="../index.html#products">Products</a>
                <a href="../tools/yield-estimator.html">Yield Estimator</a>
                <a href="../tools/wellness-stack-builder.html">Stack Builder</a>
                <a href="../tools/diagnostics.html">Diagnostics</a>
                <a href="index.html" class="active">Blog</a>
            </div>
        </div>
    </nav>

    <!-- ═══ ARTICLE CONTENT ═══ -->
    <main class="blog-container">
        <article class="blog-post">
            <header class="blog-header-section">
                <h1 class="blog-title">{title}</h1>
                <div class="blog-meta">
                    <span class="blog-author">By {author}</span>
                    <span class="blog-date">{date}</span>
                </div>
            </header>
            
            <div class="blog-body">
                {body}
            </div>

            <footer class="blog-footer-cta">
                <div>
                    <h4>Explore Science-Backed Solutions</h4>
                    <p>{cta_desc}</p>
                </div>
                <a href="{cta_url}" class="btn-blog-cta">{cta_btn}</a>
            </footer>
        </article>
    </main>

    <!-- ═══ FOOTER ═══ -->
    <footer style="background:var(--green-dark); color:var(--text-on-dark); padding:60px 0; text-align:center;">
        <div class="container">
            <a href="../index.html" style="display:inline-flex; align-items:center; gap:12px; text-decoration:none; margin-bottom:24px;">
                <img src="../assets/icon-128.png" alt="SporlyWorks" style="height:32px; width:32px;">
                <span style="color:var(--gold-light); letter-spacing:3px;">SPORLYWORKS</span>
            </a>
            <p style="color:var(--text-on-dark); opacity:0.6; font-size:12px; max-width:600px; margin:0 auto 12px;">Affiliate Disclosure: We may earn a referral commission when you purchase through our links at no additional cost to you.</p>
            <p style="color:var(--text-on-dark); opacity:0.6; font-size:11px;">&copy; 2026 SporlyWorks. All rights reserved.</p>
        </div>
    </footer>

</body>
</html>
"""

# Template for blog index list page
INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SporlyWorks Blog — Science-Backed Mycology & Functional Nutrition</title>
    <meta name="description" content="Explore peer-reviewed articles and grow logs from the SporlyWorks science board. Discover neurogenesis, survivability, and cultivation guides.">
    <link rel="icon" type="image/x-icon" href="../assets/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{style_path}">
    <style>
        .blog-index-container {{
            max-width: 1000px;
            margin: 140px auto 80px;
            padding: 0 24px;
        }}
        .blog-index-header {{
            text-align: center;
            margin-bottom: 60px;
        }}
        .blog-index-title {{
            font-family: 'Cinzel', serif;
            font-size: 40px;
            color: var(--green-dark);
            margin-bottom: 16px;
        }}
        .blog-index-subtitle {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 20px;
            color: var(--text-muted);
            font-style: italic;
        }}
        .blog-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 32px;
        }}
        @media (min-width: 768px) {{
            .blog-grid {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
        .blog-card {{
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 32px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.4s var(--transition-smooth);
            text-decoration: none;
            color: inherit;
        }}
        .blog-card:hover {{
            transform: translateY(-4px);
            border-color: var(--green-dark);
            box-shadow: 0 12px 32px rgba(44, 36, 24, 0.05);
        }}
        .card-top {{
            margin-bottom: 24px;
        }}
        .card-meta {{
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
            display: block;
        }}
        .card-title {{
            font-family: 'Cinzel', serif;
            font-size: 20px;
            color: var(--green-dark);
            margin-bottom: 12px;
            line-height: 1.4;
        }}
        .card-summary {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 17px;
            line-height: 1.5;
            color: var(--text-dark);
        }}
        .card-read-more {{
            font-family: 'Cinzel', serif;
            font-size: 13px;
            font-weight: 700;
            color: var(--gold-dark);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
    </style>
</head>
<body>

    <!-- ═══ NAVIGATION ═══ -->
    <nav id="mainNav" class="scrolled">
        <div class="nav-inner">
            <a href="../index.html" class="nav-brand">
                <img src="../assets/icon-128.png" alt="SporlyWorks" class="nav-icon">
                <span class="nav-wordmark" style="font-size:24px;">SPORLYWORKS</span>
            </a>
            <div class="nav-links">
                <a href="../index.html#products">Products</a>
                <a href="../tools/yield-estimator.html">Yield Estimator</a>
                <a href="../tools/wellness-stack-builder.html">Stack Builder</a>
                <a href="../tools/diagnostics.html">Diagnostics</a>
                <a href="index.html" class="active">Blog</a>
            </div>
        </div>
    </nav>

    <!-- ═══ BLOG INDEX ═══ -->
    <main class="blog-index-container">
        <header class="blog-index-header">
            <h1 class="blog-index-title">Scientific Library</h1>
            <p class="blog-index-subtitle">Vetted clinical analyses, grow diagnostics, and formulation studies</p>
        </header>

        <div class="blog-grid">
            {cards}
        </div>
    </main>

    <!-- ═══ FOOTER ═══ -->
    <footer style="background:var(--green-dark); color:var(--text-on-dark); padding:60px 0; text-align:center;">
        <div class="container">
            <a href="../index.html" style="display:inline-flex; align-items:center; gap:12px; text-decoration:none; margin-bottom:24px;">
                <img src="../assets/icon-128.png" alt="SporlyWorks" style="height:32px; width:32px;">
                <span style="color:var(--gold-light); letter-spacing:3px;">SPORLYWORKS</span>
            </a>
            <p style="color:var(--text-on-dark); opacity:0.6; font-size:12px; max-width:600px; margin:0 auto 12px;">Affiliate Disclosure: We may earn a referral commission when you purchase through our links at no additional cost to you.</p>
            <p style="color:var(--text-on-dark); opacity:0.6; font-size:11px;">&copy; 2026 SporlyWorks. All rights reserved.</p>
        </div>
    </footer>

</body>
</html>
"""

def generate_blog():
    articles = []
    
    # Scan Markdown files
    for filename in sorted(os.listdir(ARTICLES_DIR)):
        if filename.endswith(".md"):
            filepath = os.path.join(ARTICLES_DIR, filename)
            slug = filename[:-3]
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse Frontmatter
            frontmatter = {}
            body_md = content
            
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    body_md = parts[2]
                    for line in parts[1].strip().split("\n"):
                        if ":" in line:
                            k, v = line.split(":", 1)
                            frontmatter[k.strip()] = v.strip().replace('"', '')

            title = frontmatter.get("title", "Mycology Research Post")
            date = frontmatter.get("date", "2026-07-11")
            author = frontmatter.get("author", "David Mahler")
            summary = frontmatter.get("summary", "")
            keywords = frontmatter.get("keywords", "")

            # Set Conversion Optimized Calls-To-Action based on keywords
            cta_desc = "Optimize your biological absorption with verified organic functional supplements."
            cta_url = "../products/lions-mane-extract.html"
            cta_btn = "Shop Lion's Mane Extract →"
            
            if "lions" in keywords.lower():
                cta_desc = "Grow premium Hericium erinaceus right at home. Fully colonized and 100% guaranteed."
                cta_url = "../products/lions-mane-grow-kit.html"
                cta_btn = "Shop Lion's Mane Kit →"
            elif "contamination" in keywords.lower() or "grow" in keywords.lower():
                cta_desc = "Start your cultivation with our professional, pre-sterilized all-in-one bags."
                cta_url = "../products/magic-bag-grow-bags.html"
                cta_btn = "Get Magic Bags →"
            elif "synbiotics" in keywords.lower() or "probiotic" in keywords.lower():
                cta_desc = "Shield your gut system using Seed's dual-capsule engineered delivery."
                cta_url = "../products/seed-ds01.html"
                cta_btn = "Get Seed DS-01 →"

            # Parse MD to HTML
            body_html = parse_markdown(body_md)

            # Format Page HTML
            page_html = ARTICLE_TEMPLATE.format(
                title=title,
                description=summary,
                keywords=keywords,
                slug=slug,
                favicon=FAVICON_PATH,
                style_path=STYLE_PATH,
                author=author,
                date=date,
                body=body_html,
                cta_desc=cta_desc,
                cta_url=cta_url,
                cta_btn=cta_btn
            )

            # Output HTML page
            out_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(page_html)
            print(f"Generated Blog Post: {out_path}")
            
            articles.append({
                "slug": slug,
                "title": title,
                "date": date,
                "summary": summary
            })

    # Generate Index list page
    cards_html = ""
    for art in articles:
        cards_html += f"""
        <a href="{art['slug']}.html" class="blog-card">
            <div class="card-top">
                <span class="card-meta">{art['date']}</span>
                <h3 class="card-title">{art['title']}</h3>
                <p class="card-summary">{art['summary']}</p>
            </div>
            <span class="card-read-more">Read Research Paper →</span>
        </a>
        """
        
    index_html = INDEX_TEMPLATE.format(
        style_path=STYLE_PATH,
        cards=cards_html
    )
    
    index_out = os.path.join(OUTPUT_DIR, "index.html")
    with open(index_out, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"Generated Blog Index: {index_out}")

if __name__ == "__main__":
    generate_blog()
