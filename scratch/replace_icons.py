import re
import os

with open('/Users/davidmahler/Desktop/microAssets/_landing_page/index.html', 'r') as f:
    content = f.read()

def repl(match):
    app_name = match.group(1)
    full_match = match.group(0)
    
    img_tag = f'<span class="ext-icon"><img src="../{app_name}/icons/icon_spore.svg" alt="icon" style="width: 32px; height: 32px; border-radius: 4px;"></span>'
    
    return re.sub(r'<span class="ext-icon">.*?</span>', img_tag, full_match, count=1, flags=re.DOTALL)

pattern = r'<a[^>]*data-app="([^"]+)"[^>]*>\s*<span class="ext-icon">.*?</span>'
new_content = re.sub(pattern, repl, content, flags=re.DOTALL)

with open('/Users/davidmahler/Desktop/microAssets/_landing_page/index.html', 'w') as f:
    f.write(new_content)

print("Icons replaced.")
