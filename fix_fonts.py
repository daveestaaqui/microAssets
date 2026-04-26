import re

def update_files():
    # 1. Update index.html to remove the text "SporlyWorks" and let the logo-nav handle it
    with open("index.html", "r") as f:
        content = f.read()
    
    # Remove the span/div that adds the text next to the image, since the image now contains the text
    pattern = r'<div style="display: flex; align-items: center; margin-left: 14px;">\s*<span class="company-name" style="margin-left: 0; font-weight: 700; letter-spacing: -0.5px;">SporlyWorks</span>\s*</div>'
    new_content = re.sub(pattern, '', content)
    
    # Also update the img to show the whole logo
    new_content = new_content.replace('alt="SporlyWorks S Logo"', 'alt="SporlyWorks Logo"')
    
    if new_content != content:
        with open("index.html", "w") as f:
            f.write(new_content)
        print("Updated index.html to use image-only navigation branding.")

    # 2. Update style.css to use Inter for company-name (fallback if still used elsewhere)
    with open("style.css", "r") as f:
        style = f.read()
    
    style = style.replace("font-family: 'DM Serif Display', serif;", "font-family: 'Inter', sans-serif;")
    
    with open("style.css", "w") as f:
        f.write(style)
    print("Updated style.css to use Inter (modern sans-serif) for company-name.")

if __name__ == "__main__":
    update_files()
