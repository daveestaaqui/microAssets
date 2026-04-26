import re

with open('marketing/portfolio_pruning_report.json') as f:
    import json
    data = json.load(f)
    apps_to_remove = data['cut_candidates']

with open('_landing_page/index.html', 'r') as f:
    content = f.read()

for app in apps_to_remove:
    # Match the <a ... data-app="app" ...> ... </a>
    pattern = r'<a[^>]*data-app="' + re.escape(app) + r'"[^>]*>.*?</a>\n*'
    content = re.sub(pattern, '', content, flags=re.DOTALL)

with open('_landing_page/index.html', 'w') as f:
    f.write(content)

print("Removed 19 apps from index.html")
