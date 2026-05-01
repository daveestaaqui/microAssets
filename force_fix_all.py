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
    # Only keep cache buster for the landing page
    h_path = "_landing_page/index.html"
    if not os.path.exists(h_path): return
    with open(h_path, "r") as f:
        html = f.read()
    
    import time
    buster = str(int(time.time()))
    html = re.sub(r'logo-nav.png\?v=\d+', f'logo-nav.png?v={buster}', html)
    html = re.sub(r'unified-logo.png\?v=\d+', f'unified-logo.png?v={buster}', html)
    
    with open(h_path, "w") as f:
        f.write(html)

if __name__ == "__main__":
    create_brand_assets()
    update_code()
    print("RE-FIX COMPLETE. Pushing with cache busters.")
