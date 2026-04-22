import urllib.request
from playwright.sync_api import sync_playwright

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body {{
            margin: 0; padding: 0;
            width: 512px; height: 512px;
            display: flex; justify-content: center; align-items: center;
        }}
        {CSS_STYLING}
    </style>
</head>
<body>
    <div class="canvas">
        <div class="icon-container">
            <i data-lucide="clock"></i>
        </div>
    </div>
    <script>
        lucide.createIcons();
    </script>
</body>
</html>
"""

CONCEPTS = {
    "A_Linear_Minimal": """
        .canvas { background: #000000; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
        .icon-container { width: 320px; height: 320px; background: #111111; border: 1px solid #333333; border-radius: 64px; display: flex; justify-content: center; align-items: center; }
        .icon-container svg { color: #FFFFFF; width: 140px; height: 140px; stroke-width: 1.5px; }
    """,
    "B_Apple_Vibrant": """
        .canvas { background: #F5F5F7; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
        .icon-container { width: 320px; height: 320px; background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%); border-radius: 72px; display: flex; justify-content: center; align-items: center; box-shadow: 0 20px 40px rgba(0,0,0,0.15); }
        .icon-container svg { color: #FFFFFF; width: 160px; height: 160px; stroke-width: 2px; }
    """,
    "C_B2B_Enterprise": """
        .canvas { background: #FFFFFF; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
        .icon-container { width: 320px; height: 320px; background: #E8F0FE; border-radius: 32px; display: flex; justify-content: center; align-items: center; }
        .icon-container svg { color: #1A73E8; width: 160px; height: 160px; stroke-width: 2.2px; }
    """
}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 512, "height": 512})
    for name, css in CONCEPTS.items():
        page.set_content(HTML_TEMPLATE.replace("{CSS_STYLING}", css))
        page.wait_for_selector('svg')
        page.screenshot(path=f"{name}.png")
    browser.close()
