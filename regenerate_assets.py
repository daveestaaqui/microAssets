from PIL import Image, ImageDraw, ImageFont
import os

def create_brand_assets():
    # 1. Master Logo (unified-logo.png)
    w, h = 1200, 600
    img = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    try:
        font_main = ImageFont.truetype(font_path, 120, index=1) 
        font_sub = ImageFont.truetype(font_path, 52, index=0)
    except:
        font_main = ImageFont.load_default(size=120)
        font_sub = ImageFont.load_default(size=52)

    # Paste "S" Spore graphic
    s_path = "_landing_page/logo-256.png"
    if os.path.exists(s_path):
        s_img = Image.open(s_path).convert("RGBA")
        s_img.thumbnail((300, 300), Image.Resampling.LANCZOS)
        img.paste(s_img, ((w - s_img.width)//2, 30), s_img)
    
    # Text: SporlyWorks
    color = (26, 26, 26, 255)
    name_w = draw.textlength("SporlyWorks", font=font_main)
    draw.text(((w - name_w)//2, 350), "SporlyWorks", font=font_main, fill=color)
    
    # Slogan: cultivating intelligent workflows.
    sub_color = (80, 80, 80, 255)
    slogan = "cultivating intelligent workflows."
    slogan_w = draw.textlength(slogan, font=font_sub)
    draw.text(((w - slogan_w)//2, 480), slogan, font=font_sub, fill=sub_color)
    
    img.save("_landing_page/unified-logo.png", "PNG")
    print("Regenerated unified-logo.png with slogan: 'cultivating intelligent workflows.'")

    # 2. Large Nav Logo (logo-nav.png)
    # User can't tell what it is -> Make it even larger and ensure TRUE transparency
    nav_size = 512
    nav_img = Image.new('RGBA', (nav_size, nav_size), (255, 255, 255, 0))
    if os.path.exists(s_path):
        s_img = Image.open(s_path).convert("RGBA")
        s_img = s_img.resize((nav_size, nav_size), Image.Resampling.LANCZOS)
        nav_img.paste(s_img, (0, 0), s_img)
        nav_img.save("_landing_page/logo-nav.png", "PNG")
        print("Regenerated logo-nav.png at 512x512 with true transparency.")

if __name__ == "__main__":
    create_brand_assets()
