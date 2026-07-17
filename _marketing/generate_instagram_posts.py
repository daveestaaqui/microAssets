import os
import sys
import re
from PIL import Image, ImageDraw, ImageFont

# Set paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS_DIR = os.path.join(BASE_DIR, "_marketing", "instagram_drafts")
os.makedirs(DRAFTS_DIR, exist_ok=True)

# Select Fonts
FONT_SERIF_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"
FONT_SANS_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        return ImageFont.load_default()

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        line_str = " ".join(current_line)
        bbox = draw.textbbox((0, 0), line_str, font=font)
        w = bbox[2] - bbox[0]
        if w > max_width:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))
    return lines

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
            # Resize to 90x90
            logo_img = logo_img.resize((90, 90), Image.Resampling.LANCZOS)
            # Paste logo centered at top (Y=70)
            logo_x = (width - 90) // 2
            img.paste(logo_img, (logo_x, 70), logo_img)
            logo_placed = True
        except Exception as e:
            print(f"⚠️ Error pasting logo: {e}")
            
    # 3. Header Text under Logo
    header_y = 195 if logo_placed else 100
    header_font = get_font(FONT_SERIF_PATH, 26)
    draw.text((width // 2, header_y), "SPORLYWORKS", fill=gold, font=header_font, anchor="mm")
    
    # Draw small botanical line decoration under header
    draw.line([(width // 2) - 80, header_y + 25, (width // 2) + 80, header_y + 25], fill=gold, width=1)
    
    # 4. Small Category/Title Label
    cat_font = get_font(FONT_SANS_PATH, 20)
    draw.text((width // 2, header_y + 80), title.upper(), fill=forest_green, font=cat_font, anchor="mm")
    
    # 5. Main Big Quote Text (Editorial style, much bigger text, shorter copy)
    quote_font = get_font(FONT_SERIF_PATH, 42)
    wrapped_lines = wrap_text(quote, quote_font, 820, draw)
    
    # Calculate starting Y to center the block vertically in the remaining space
    total_text_height = len(wrapped_lines) * 60
    content_center_y = 560
    start_y = content_center_y - (total_text_height // 2)
    
    for idx, line in enumerate(wrapped_lines):
        line_y = start_y + (idx * 60)
        draw.text((width // 2, line_y), line, fill=deep_green, font=quote_font, anchor="mm")
        
    # 6. Source citation at bottom of main content area
    source_font = get_font(FONT_SANS_PATH, 20)
    draw.text((width // 2, 850), f"Source: {source}", fill=gold, font=source_font, anchor="mm")
    
    # 7. Editorial Footer
    footer_text = "BOTANICAL PRECISION × FUNCTIONAL WELLNESS"
    footer_font = get_font(FONT_SANS_PATH, 16)
    draw.text((width // 2, 1000), footer_text, fill=forest_green, font=footer_font, anchor="mm")
    
    # Save Image
    img_path = os.path.join(DRAFTS_DIR, f"{output_name}.jpg")
    img.save(img_path, "JPEG", quality=95)
    print(f"Generated post image: {img_path}")

# Post 1
draw_post(
    title="Clinical Adaptogens",
    quote="“Lion’s Mane contains active hericenones that pass the blood-brain barrier to directly stimulate Nerve Growth Factor (NGF) synthesis.”",
    source="Mori, K., et al. (2009) | Phytotherapy Research",
    output_name="post1"
)

# Post 2
draw_post(
    title="Cultivation Science",
    quote="“Biological Efficiency (BE) measures the ratio of fresh mushroom weight relative to the dry weight of substrate used.”",
    source="Stamets, P. (2000) | Growing Gourmet & Medicinal Mushrooms",
    output_name="post2"
)

# Post 3
draw_post(
    title="Supplement Purity",
    quote="“Premium adaptogens use 100% organic fruiting bodies. Avoid brands that grind mycelium-on-grain starch fillers into your supplement.”",
    source="FreshCap Botanical Standards | freshcap.com",
    output_name="post3"
)

# Captions with official URL references and citations in descriptions
captions = {
    "post1": """🧠 CEREBRAL PRECISION: Nerve Growth Factor (NGF) & Neurogenesis

Active compounds found in Lion’s Mane mushroom (Hericium erinaceus) have been clinically shown to cross the blood-brain barrier, triggering the natural production of Nerve Growth Factor (NGF). 

NGF plays a critical role in the growth, maintenance, and survival of cholinergic neurons, supporting focus, memory retention, and cognitive longevity.

🔬 Scientific Source:
Mori, K., Inatomi, S., Ouchi, K., Azumi, Y., & Tuchida, T. (2009). Improving effects of the mushroom Yamabushitake (Hericium erinaceus) on mild cognitive impairment: a double-blind placebo-controlled clinical trial. Phytotherapy Research, 23(3), 367-372.
🔗 Study Link: https://pubmed.ncbi.nlm.nih.gov/18844328/

Learn more about adaptogenic chemistry at sporlyworks.com

#functionalmushrooms #adaptogens #lionsmane #neurogenesis #brainhealth #apothecary #cognitivescience #clinicaltrials #sporlyworks""",

    "post2": """🍄 LAB PROFILE: Biological Efficiency (BE) in Mushroom Cultivation

Biological Efficiency (BE) is the standard metric used by commercial and home laboratories to measure spawn performance. It represents the ratio of fresh mushroom harvest weight relative to the dry weight of substrate used. 

Achieving high BE (>80%) requires precise hydration (field capacity), professional spawn inoculation, and sterile HEPA flow environments.

🔬 Scientific Source:
Stamets, P. (2000). Growing Gourmet and Medicinal Mushrooms (3rd ed.). Ten Speed Press.

Simplify your home laboratory parameters with our free Substrate Calculator and Yield Estimator tools at sporlyworks.com

#mushroomcultivation #mycologysociety #homebiology #spores #steriletechnique #mycelium #fungi #growblocks #sporlyworks""",

    "post3": """🛡️ DIETARY SUPPLEMENT PURITY: Fruiting Body vs. Starch Fillers

Many retail mushroom powders are 'mycelium on grain' products. This means the active mycelium is grown on rice, oats, or sorghum, and the starch-heavy grain is ground up directly into your supplement—often resulting in up to 70% inactive fillers.

True therapeutic benefit comes from 100% organic fruiting bodies (the actual mushroom), hot-water extracted to break down indigestible chitin walls and release pure beta-glucans.

🔬 Scientific Source:
FreshCap Mushroom Quality & Purity Standards. Read the scientific research and clinical analysis of beta-glucans at: https://freshcap.com/pages/clinical-research

🔗 Find verified fruiting-body extracts at sporlyworks.com

#functionalmushrooms #adaptogens #reishi #cordyceps #lionsmane #freshcap #immunesupport #supplementpurity #cleanlabel #sporlyworks"""
}

for name, text in captions.items():
    cap_path = os.path.join(DRAFTS_DIR, f"{name}.txt")
    with open(cap_path, "w") as f:
        f.write(text)
    print(f"Generated post caption: {cap_path}")
