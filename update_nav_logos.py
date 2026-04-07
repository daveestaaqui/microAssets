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

            # We only replace if the block contains "SporlyWorks logo" or "company-name"
            # to ensure we don't overwrite if it was already updated
            def replacer(m):
                original_block = m.group(0)
                if 'company-name' in original_block or 'logo-64.png' in original_block:
                    return f'<a href="{m.group(1)}index.html" class="nav-logo" style="text-decoration: none; padding: 6px 0;">\n                <img src="{m.group(1)}unified-logo.png?v=23" alt="SporlyWorks" style="height: 36px; width: auto; object-fit: contain;">\n            </a>'
                return original_block

            new_content = pattern.sub(replacer, content)

            if new_content != content:
                with open(filepath, 'w') as f:
                    f.write(new_content)
                count += 1
                print(f"Updated {file}")

print(f"Total files updated: {count}")
