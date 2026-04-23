import re

def update():
    # 1. HTML - Make nav logo MASSIVE so it's unmistakable
    html_path = "_landing_page/index.html"
    with open(html_path, "r") as f:
        html = f.read()
    
    # Increase height in nav from 80 to 120
    html = html.replace('height="80"', 'height="120"')
    # Ensure correct alt text
    html = html.replace('alt="SporlyWorks — cultivating intelligent workflows."', 'alt="SporlyWorks — cultivating intelligent workflows."')
    
    with open(html_path, "w") as f:
        f.write(html)

    # 2. CSS - Force transparency and adjust spacing for the larger logo
    css_path = "_landing_page/style.css"
    with open(css_path, "r") as f:
        css = f.read()
    
    # Remove any filters or blend modes that might add a "haze" or background
    css = re.sub(r'mix-blend-mode: [^;]+;', '', css)
    css = re.sub(r'filter: [^;]+;', '', css)
    
    # Ensure nav-logo doesn't have a background or border
    css += "\n.nav-logo img { background: transparent !important; border: none !important; box-shadow: none !important; }\n"
    
    with open(css_path, "w") as f:
        f.write(css)

    print("Updated HTML/CSS for unmistakable logo visibility.")

if __name__ == "__main__":
    update()
