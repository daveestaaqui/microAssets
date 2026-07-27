import os
import sys
import re
import glob
from PIL import Image, ImageDraw, ImageFont

# Set paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PINTEREST_DRAFTS_DIR = os.path.join(BASE_DIR, "_marketing", "pinterest_drafts")
BLOG_DIR = os.path.join(BASE_DIR, "blog", "articles")
os.makedirs(PINTEREST_DRAFTS_DIR, exist_ok=True)

# Select Fonts
FONT_SERIF_PATHS = [
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
]
FONT_SANS_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]

LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")

def get_font(paths, size):
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except IOError:
            continue
    return ImageFont.load_default()

def wrap_text(text, font, max_width, draw):
    if not text:
        return []
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        line_str = " ".join(current_line)
        bbox = draw.textbbox((0, 0), line_str, font=font)
        w = bbox[2] - bbox[0]
        if w > max_width:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(" ".join(current_line))
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def parse_frontmatter(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    parts = content.split("---")
    if len(parts) >= 3:
        frontmatter = parts[1]
        data = {}
        for line in frontmatter.strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                data[key.strip()] = val.strip().strip('"').strip("'")
        return data
    return {}

def draw_pinterest_pin(title, summary, output_name):
    # Dimensions (1000x1500 Vertical Pin)
    width, height = 1000, 1500
    
    # Cream Background
    img = Image.new("RGB", (width, height), "#FCFAF6")
    draw = ImageDraw.Draw(img)
    
    # Colors
    forest_green = "#2C4A3E"
    gold = "#C9A84C"
    
    # Borders
    draw.rectangle([40, 40, 960, 1460], outline=forest_green, width=3)
    draw.rectangle([60, 60, 940, 1440], outline=gold, width=1)
    
    # Paste Logo
    logo_placed = False
    if os.path.exists(LOGO_PATH):
        try:
            logo_img = Image.open(LOGO_PATH).convert("RGBA")
            logo_img = logo_img.resize((120, 120), Image.Resampling.LANCZOS)
            logo_x = (width - 120) // 2
            img.paste(logo_img, (logo_x, 100), logo_img)
            logo_placed = True
        except Exception as e:
            print(f"⚠️ Error pasting logo: {e}")
            
    # Title Text
    title_y = 280 if logo_placed else 200
    title_font = get_font(FONT_SERIF_PATHS, 60)
    wrapped_title = wrap_text(title.upper(), title_font, 800, draw)
    
    for idx, line in enumerate(wrapped_title):
        line_y = title_y + (idx * 75)
        draw.text((width // 2, line_y), line, fill=forest_green, font=title_font, anchor="mm")
    
    # Summary Text in middle
    summary_font = get_font(FONT_SERIF_PATHS, 36)
    wrapped_summary = wrap_text(summary, summary_font, 700, draw)
    
    content_center_y = 850
    total_summary_height = len(wrapped_summary) * 50
    start_summary_y = content_center_y - (total_summary_height // 2)
    
    for idx, line in enumerate(wrapped_summary):
        line_y = start_summary_y + (idx * 50)
        draw.text((width // 2, line_y), line, fill="#4A4A4A", font=summary_font, anchor="mm")
        
    # Footer
    footer_text = "sporlyworks.com"
    footer_font = get_font(FONT_SANS_PATHS, 24)
    draw.text((width // 2, 1380), footer_text, fill=forest_green, font=footer_font, anchor="mm")
    
    # Save Image
    img_path = os.path.join(PINTEREST_DRAFTS_DIR, f"{output_name}.jpg")
    img.save(img_path, "JPEG", quality=95)
    print(f"Generated pinterest pin image: {img_path}")

def generate_pin_description(title, keywords, slug):
    kw_tags = " ".join([f"#{k.strip().replace(' ', '')}" for k in keywords.split(",") if k.strip()])
    return f"{title}\n\nRead the full guide on sporlyworks.com/blog/{slug}\n\n{kw_tags} #sporlyworks"

def main():
    if not os.path.exists(BLOG_DIR):
        print(f"No blog directory found at {BLOG_DIR}")
        return
        
    for md_file in glob.glob(os.path.join(BLOG_DIR, "*.md")):
        slug = os.path.splitext(os.path.basename(md_file))[0]
        data = parse_frontmatter(md_file)
        
        title = data.get("title", "SporlyWorks Guide")
        summary = data.get("summary", "")
        keywords = data.get("keywords", "wellness, adaptogens")
        
        if not title:
            continue
            
        draw_pinterest_pin(
            title=title,
            summary=summary,
            output_name=f"pin_{slug}"
        )
        
        desc = generate_pin_description(title, keywords, slug)
        desc_path = os.path.join(PINTEREST_DRAFTS_DIR, f"pin_{slug}.txt")
        with open(desc_path, "w", encoding="utf-8") as f:
            f.write(desc)
        print(f"Generated pin description: {desc_path}")

if __name__ == "__main__":
    main()
