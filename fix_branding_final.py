from PIL import Image, ImageDraw, ImageFont
import os

def generate_logo(filename, brand_name, slogan_text):
    # Dimensions
    width, height = 1200, 600
    # Ensuring TRUE transparency
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Use a high-quality system font or Inter if available
    font_path = "/System/Library/Fonts/Helvetica.ttc" # Standard Mac font
    if not os.path.exists(font_path):
        font_path = None # Fallback

    try:
        font_main = ImageFont.truetype(font_path, 110, index=1) if font_path else ImageFont.load_default(size=110)
        font_sub = ImageFont.truetype(font_path, 48, index=0) if font_path else ImageFont.load_default(size=48)
    except:
        font_main = ImageFont.load_default(size=110)
        font_sub = ImageFont.load_default(size=48)

    # 1. Base Logo Graphic (The "S" Spore)
    s_logo_path = "_landing_page/logo-256.png"
    if os.path.exists(s_logo_path):
        s_logo = Image.open(s_logo_path).convert("RGBA")
        s_logo.thumbnail((280, 280), Image.Resampling.LANCZOS)
        # Paste centered at the top
        img.paste(s_logo, ((width - s_logo.width)//2, 40), s_logo)
    
    # 2. Brand Name
    text_color = (26, 26, 26, 255) # Charcoal
    name_w = draw.textlength(brand_name, font=font_main)
    draw.text(((width - name_w)//2, 340), brand_name, font=font_main, fill=text_color)
    
    # 3. CORRECT Slogan: "cultivating intelligent workflows."
    slogan_color = (74, 74, 74, 255) # Slate
    slogan_w = draw.textlength(slogan_text, font=font_sub)
    draw.text(((width - slogan_w)//2, 460), slogan_text, font=font_sub, fill=slogan_color)
    
    img.save(f"_landing_page/{filename}", "PNG")
    print(f"Verified & Created: _landing_page/{filename} with slogan: '{slogan_text}'")

def fix_nav_logo():
    # Large 512x512 transparent nav logo
    size = 512
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    src_path = "_landing_page/logo-256.png"
    if os.path.exists(src_path):
        src = Image.open(src_path).convert("RGBA")
        src = src.resize((size, size), Image.Resampling.LANCZOS)
        img.paste(src, (0, 0), src)
        img.save("_landing_page/logo-nav.png", "PNG")
        print("Fixed nav logo size and verified transparency.")

if __name__ == "__main__":
    # Ensure correct spelling: "cultivating intelligent workflows."
    generate_logo("unified-logo.png", "SporlyWorks", "cultivating intelligent workflows.")
    generate_logo("omnisuite-logo.png", "OmniSuite", "the complete developer toolkit.")
    fix_nav_logo()
