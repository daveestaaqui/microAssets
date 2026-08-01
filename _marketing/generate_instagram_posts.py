import os
import sys
import re
import glob
from PIL import Image, ImageDraw, ImageFont

# Set paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS_DIR = os.path.join(BASE_DIR, "_marketing", "instagram_drafts")
BLOG_DIR = os.path.join(BASE_DIR, "blog", "articles")
os.makedirs(DRAFTS_DIR, exist_ok=True)

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

def draw_post(title, quote, source, output_name):
    # Dimensions (1080x1080 Square Post)
    width, height = 1080, 1080
    
    # Cream Background
    img = Image.new("RGB", (width, height), "#FCFAF6")
    draw = ImageDraw.Draw(img)
    
    # Colors
    forest_green = "#1B8A5A"
    deep_green = "#0D3321"
    gold = "#C9A84C"
    charcoal = "#2C3531"
    
    # 1. Outer Borders
    draw.rectangle([20, 20, 1060, 1060], outline=forest_green, width=2)
    draw.rectangle([35, 35, 1045, 1045], outline=gold, width=1)
    
    # 2. Paste Branded SporlyWorks Logo
    logo_placed = False
    if os.path.exists(LOGO_PATH):
        try:
            logo_img = Image.open(LOGO_PATH).convert("RGBA")
            import numpy as np
            arr = np.array(logo_img)
            black_pixels = (arr[:,:,0] < 35) & (arr[:,:,1] < 35) & (arr[:,:,2] < 35)
            arr[black_pixels, 3] = 0
            cleaned_logo = Image.fromarray(arr)
            
            # Resize to 90x90
            logo_scaled = cleaned_logo.resize((90, 90), Image.Resampling.LANCZOS)
            # Paste logo centered at top (Y=70)
            logo_x = (width - 90) // 2
            img.paste(logo_scaled, (logo_x, 70), logo_scaled)
            logo_placed = True
        except Exception as e:
            print(f"⚠️ Error pasting logo: {e}")
            
    # 3. Header Text under Logo
    header_y = 195 if logo_placed else 100
    header_font = get_font(FONT_SERIF_PATHS, 26)
    draw.text((width // 2, header_y), "SPORLYWORKS", fill=gold, font=header_font, anchor="mm")
    
    # Draw small botanical line decoration under header
    draw.line([(width // 2) - 80, header_y + 25, (width // 2) + 80, header_y + 25], fill=gold, width=1)
    
    # 4. Small Category/Title Label
    cat_font = get_font(FONT_SANS_PATHS, 20)
    draw.text((width // 2, header_y + 80), title.upper()[:40], fill=forest_green, font=cat_font, anchor="mm")
    
    # 5. Main Big Quote Text (Editorial style, much bigger text, shorter copy)
    quote_font = get_font(FONT_SERIF_PATHS, 42)
    wrapped_lines = wrap_text(f"“{quote}”", quote_font, 820, draw)
    
    # Calculate starting Y to center the block vertically in the remaining space
    total_text_height = len(wrapped_lines) * 60
    content_center_y = 560
    start_y = content_center_y - (total_text_height // 2)
    
    for idx, line in enumerate(wrapped_lines):
        line_y = start_y + (idx * 60)
        draw.text((width // 2, line_y), line, fill=deep_green, font=quote_font, anchor="mm")
        
    # 6. Source citation at bottom of main content area
    source_font = get_font(FONT_SANS_PATHS, 20)
    draw.text((width // 2, 850), f"Source: {source}", fill=gold, font=source_font, anchor="mm")
    
    # 7. Editorial Footer
    footer_text = "BOTANICAL PRECISION × FUNCTIONAL WELLNESS"
    footer_font = get_font(FONT_SANS_PATHS, 16)
    draw.text((width // 2, 1000), footer_text, fill=forest_green, font=footer_font, anchor="mm")
    
    # Save Image
    img_path = os.path.join(DRAFTS_DIR, f"{output_name}.jpg")
    img.save(img_path, "JPEG", quality=95)
    print(f"Generated post image: {img_path}")

def generate_caption(title, keywords, slug):
    kw_tags = " ".join([f"#{k.strip().replace(' ', '')}" for k in keywords.split(",") if k.strip()])
    return f"{title}\n\nRead the full article at sporlyworks.com/blog/{slug}\n\n{kw_tags} #sporlyworks"

def main():
    if not os.path.exists(BLOG_DIR):
        print(f"No blog directory found at {BLOG_DIR}")
        return
        
    for md_file in glob.glob(os.path.join(BLOG_DIR, "*.md")):
        slug = os.path.splitext(os.path.basename(md_file))[0]
        data = parse_frontmatter(md_file)
        
        title = data.get("title", "SporlyWorks Journal")
        summary = data.get("summary", "")
        keywords = data.get("keywords", "wellness, adaptogens")
        
        if not summary:
            # Skip if no summary
            continue
            
        draw_post(
            title=title,
            quote=summary,
            source=f"sporlyworks.com/blog/{slug}",
            output_name=f"post_{slug}"
        )
        
        caption = generate_caption(title, keywords, slug)
        cap_path = os.path.join(DRAFTS_DIR, f"post_{slug}.txt")
        with open(cap_path, "w", encoding="utf-8") as f:
            f.write(caption)
        print(f"Generated post caption: {cap_path}")

if __name__ == "__main__":
    main()
