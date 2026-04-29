from PIL import Image, ImageDraw, ImageFont
import os
import re

def create_brand_assets():
    # Master Logo (unified-logo.png) - Slogan: cultivating intelligent workflows.
    w, h = 1200, 600
    img = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Force system fonts
    f_main_path = "/System/Library/Fonts/Helvetica.ttc"
    try:
        font_main = ImageFont.truetype(f_main_path, 120, index=1) 
        font_sub = ImageFont.truetype(f_main_path, 52, index=0)
    except:
        font_main = ImageFont.load_default(size=120)
        font_sub = ImageFont.load_default(size=52)

    s_path = "_landing_page/logo-256.png"
    if os.path.exists(s_path):
        s_img = Image.open(s_path).convert("RGBA")
        s_img.thumbnail((300, 300), Image.Resampling.LANCZOS)
        img.paste(s_img, ((w - s_img.width)//2, 40), s_img)
    
    text_color = (26, 26, 26, 255)
    name_w = draw.textlength("SporlyWorks", font=font_main)
    draw.text(((w - name_w)//2, 350), "SporlyWorks", font=font_main, fill=text_color)
    
    slogan = "Engineering Automation"
    slogan_w = draw.textlength(slogan, font=font_sub)
    draw.text(((w - slogan_w)//2, 480), slogan, font=font_sub, fill=(80, 80, 80, 255))
    
    img.save("_landing_page/unified-logo.png", "PNG")
    
    # Nav Logo (logo-nav.png) - Massive & Transparent
    nav_size = 512
    nav_img = Image.new('RGBA', (nav_size, nav_size), (255, 255, 255, 0))
    if os.path.exists(s_path):
        s_nav = Image.open(s_path).convert("RGBA")
        s_nav = s_nav.resize((nav_size, nav_size), Image.Resampling.LANCZOS)
        nav_img.paste(s_nav, (0, 0), s_nav)
        nav_img.save("_landing_page/logo-nav.png", "PNG")

def update_code():
    # HTML - Set height to 120 and add a cache-buster
    h_path = "_landing_page/index.html"
    with open(h_path, "r") as f:
        html = f.read()
    
    # Use a dynamic cache buster for images
    import time
    buster = str(int(time.time()))
    html = re.sub(r'logo-nav.png\?v=\d+', f'logo-nav.png?v={buster}', html)
    html = re.sub(r'unified-logo.png\?v=\d+', f'unified-logo.png?v={buster}', html)
    
    # Force the height in HTML
    html = re.sub(r'img src="logo-nav.png[^"]+" alt="SporlyWorks S Logo" height="\d+"', 
                  f'img src="logo-nav.png?v={buster}" alt="SporlyWorks S Logo" height="150"', html)
    
    with open(h_path, "w") as f:
        f.write(html)

    # CSS - Strip all transparency-breaking filters
    c_path = "_landing_page/style.css"
    with open(c_path, "r") as f:
        css = f.read()
    
    css = re.sub(r'mix-blend-mode: [^;]+;', '', css)
    css = re.sub(r'filter: [^;]+;', '', css)
    css += "\n.nav-logo img { height: 150px !important; width: auto !important; background: transparent !important; }\n"
    
    with open(c_path, "w") as f:
        f.write(css)

if __name__ == "__main__":
    create_brand_assets()
    update_code()
    print("RE-FIX COMPLETE. Pushing with cache busters.")
