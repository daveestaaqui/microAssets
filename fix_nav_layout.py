import os
import re

directory = '/Users/davidmahler/Desktop/microAssets/_landing_page'

# Pattern matches any block starting with <a href="..." class="nav-logo" ... up to </a>
pattern = re.compile(
    r'<a href="([^"]*?)index\.html"\s*class="nav-logo"[^>]*>[\s\S]*?</a>',
    re.IGNORECASE
)

count = 0
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()

            def replacer(m):
                prefix = m.group(1)
                return f'''<a href="{prefix}index.html" class="nav-logo" style="text-decoration: none; display: flex; align-items: center; gap: 12px; padding: 4px 0;">
                <img src="{prefix}logo-64.png" alt="SporlyWorks" style="height: 52px; width: auto; object-fit: contain;">
                <div style="display: flex; flex-direction: column; justify-content: center; transform: translateY(2px);">
                    <span style="font-family: 'DM Serif Display', serif; font-size: 28px; font-weight: 400; color: var(--forest-deep); line-height: 1;">SporlyWorks</span>
                    <span style="font-family: 'DM Serif Display', serif; font-size: 14px; font-weight: 400; color: var(--forest-light); letter-spacing: 0.2px; margin-top: 1px;">Cultivating Intelligent Workflows.</span>
                </div>
            </a>'''

            new_content = pattern.sub(replacer, content)

            if new_content != content:
                with open(filepath, 'w') as f:
                    f.write(new_content)
                count += 1

print(f"Total files updated: {count}")
