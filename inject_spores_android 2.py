import os
import re

BASE_DIR = "/Users/davidmahler/Desktop/microAssets/_b2b_android"

spore_css_payload = """
    <style>
      :root {
        --app-bg: #F8F5EE;
        --app-dark: #1A1A1A;
        --app-accent: #E5E0D8;
        --app-text: #2D2D2D;
      }
      body {
        background-color: var(--app-bg) !important;
        color: var(--app-text) !important;
        font-family: 'SF Pro Display', 'Inter', -apple-system, sans-serif !important;
        margin: 0;
        padding: 0;
        letter-spacing: -0.015em;
        background-image: radial-gradient(var(--app-accent) 1px, transparent 1px);
        background-size: 24px 24px;
      }
      h1, h2, h3, h4 {
        font-weight: 700 !important;
        color: var(--app-dark) !important;
        letter-spacing: -0.02em;
      }
      .logo-container, .brand-header {
        text-align: center;
        padding: 2rem 0;
      }
      .logo-container img {
        width: 120px;
        height: 120px;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        margin: 0 auto;
        display: block;
      }
      input, select, textarea {
        border: 1px solid var(--app-dark) !important;
        border-radius: 0 !important;
        background: transparent !important;
        padding: 12px 16px !important;
        font-family: inherit;
        transition: all 150ms ease;
      }
      input:focus {
        outline: none;
        box-shadow: 4px 4px 0px var(--app-accent) !important;
        transform: translate(-2px, -2px);
      }
      button, .btn {
        background: var(--app-dark) !important;
        color: var(--app-bg) !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 14px 24px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        cursor: pointer;
        transition: transform 150ms ease;
      }
      button:hover, .btn:hover {
        transform: translateY(-2px);
      }
      /* Aggressive Pro Hiding */
      .pro-upsell, .upgrade-banner, .stripe-pro {
        display: none !important;
        opacity: 0 !important;
        height: 0 !important;
        pointer-events: none !important;
      }
    </style>
"""

def inject_android_spore(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already injected
    if 'var(--app-bg)' in content and '--app-dark' in content:
        return

    # Strip existing "Get Pro Access" and Diamond icons
    content = re.sub(r'<[^>]*>.*?💎.*?Get Pro Access.*?</[^>]*>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<div[^>]*class="[^"]*upsell[^"]*"[^>]*>.*?</div>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Inject CSS before </head>
    if '</head>' in content:
        content = content.replace('</head>', f"{spore_css_payload}\n</head>")
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    modified = 0
    if not os.path.isdir(BASE_DIR):
        print(f"Android directory {BASE_DIR} not found.")
        return
        
    for item in os.listdir(BASE_DIR):
        app_dir = os.path.join(BASE_DIR, item)
        html_path = os.path.join(app_dir, 'www', 'index.html')
        
        if os.path.exists(html_path):
            inject_android_spore(html_path)
            modified += 1
            print(f"Injected Spore UI -> {item}")
            
    print(f"Finished Android Spore UI Injection. Total updated: {modified}")

if __name__ == "__main__":
    main()
