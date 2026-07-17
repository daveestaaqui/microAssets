import os
from PIL import Image, ImageDraw, ImageFont

# Set paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS_DIR = os.path.join(BASE_DIR, "_marketing", "instagram_drafts")
os.makedirs(DRAFTS_DIR, exist_ok=True)

# Select Fonts
FONT_SERIF_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"
FONT_SANS_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        return ImageFont.load_default()

def draw_post(post_id, title, subtitle, points, output_name):
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
    
    # 2. Header (Brand Logo / Name)
    header_font = get_font(FONT_SERIF_PATH, 28)
    draw.text((width // 2, 80), "S P O R L Y W O R K S", fill=gold, font=header_font, anchor="mm")
    
    # Draw small botanical line decoration under header
    draw.line([(width // 2) - 80, 110, (width // 2) + 80, 110], fill=gold, width=1)
    
    # 3. Main Title
    title_font = get_font(FONT_SERIF_PATH, 56)
    draw.text((width // 2, 220), title, fill=deep_green, font=title_font, anchor="mm")
    
    # 4. Subtitle
    subtitle_font = get_font(FONT_SANS_PATH, 22)
    draw.text((width // 2, 285), subtitle.upper(), fill=gold, font=subtitle_font, anchor="mm")
    
    # 5. Content Area
    content_y = 380
    point_font = get_font(FONT_SANS_PATH, 24)
    num_font = get_font(FONT_SERIF_PATH, 36)
    
    for idx, p in enumerate(points):
        # Draw number circle or text
        num_str = f"0{idx+1}."
        draw.text((120, content_y), num_str, fill=gold, font=num_font)
        
        # Word-wrap point text
        words = p.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            # Rough character limit per line for 24px font
            if len(" ".join(current_line)) > 55:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        # Draw text lines
        line_y = content_y - 2
        for line in lines:
            draw.text((190, line_y), line, fill=charcoal, font=point_font)
            line_y += 38
            
        content_y += max(120, len(lines) * 42 + 40)
        
    # 6. Footer Decoration
    footer_text = "BOTANICAL PRECISION × FUNCTIONAL WELLNESS"
    footer_font = get_font(FONT_SANS_PATH, 16)
    draw.text((width // 2, 1000), footer_text, fill=forest_green, font=footer_font, anchor="mm")
    
    # Save Image
    img_path = os.path.join(DRAFTS_DIR, f"{output_name}.jpg")
    img.save(img_path, "JPEG", quality=95)
    print(f"Generated post image: {img_path}")

# Post 1 Data
draw_post(
    post_id=1,
    title="Nerve Growth Factor (NGF)",
    subtitle="Brain Cell Regeneration & focus",
    points=[
        "NGF is a crucial peptide that regulates the growth, maintenance, and survival of neurons in the central nervous system.",
        "Clinical trials show that Lion's Mane mushroom contains active hericenones that pass the blood-brain barrier directly.",
        "Consistent daily consumption supports cognitive recall, long-term memory, and neurogenesis.",
    ],
    output_name="post1"
)

# Post 2 Data
draw_post(
    post_id=2,
    title="Biological Efficiency (BE)",
    subtitle="The Science of Mycological Yields",
    points=[
        "BE measures the ratio of fresh mushroom harvest weight relative to the dry weight of the substrate used (e.g. hardwood sawdust).",
        "Hitting 75% to 100% BE requires cleanroom inoculation to prevent pathogen competition.",
        "Pre-colonized spawn blocks bypass sterile-critical stages, guaranteeing high yields immediately at home.",
    ],
    output_name="post2"
)

# Post 3 Data
draw_post(
    post_id=3,
    title="Beta-Glucans vs. Starch Fillers",
    subtitle="How to Identify Clean Supplements",
    points=[
        "Mass-market brands grow mycelium on grain (rice or oats), grinding the starchy substrate into the final powder.",
        "Verified adaptogens use 100% organic fruiting bodies (mushrooms) hot-water extracted to break down cell walls.",
        "Look for labels with verified beta-glucan content and zero starch, grain, or mycelium fillers.",
    ],
    output_name="post3"
)

# Create Caption Text Files
captions = {
    "post1": """🧠 CEREBRAL PRECISION: The Science of Nerve Growth Factor (NGF)

Can we stimulate brain cell regeneration? Modern clinical studies say yes.

Lion’s Mane mushroom (Hericium erinaceus) contains active compounds called hericenones and erinacines. These low-molecular-weight compounds cross the blood-brain barrier to stimulate the synthesis of Nerve Growth Factor (NGF) in brain cells.

💡 Clinical Study Ref: Mori, K., et al. (2009). Phytotherapy Research.
🔗 Read our comprehensive scientific breakdown at sporlyworks.com

#functionalmushrooms #adaptogens #lionsmane #neurogenesis #brainhealth #apothecary #cognitivescience #sporlyworks""",

    "post2": """🍄 LAB PROFILE: Biological Efficiency (BE) in Cultivation

Maximizing yields is about substrate biology. 

Biological Efficiency (BE) defines the ratio of fresh mushroom harvest to the dry weight of substrate used. Under optimal sterile conditions with HEPA flow hoods, gourmet blocks hit 70-100% efficiency.

🔬 Learn the mathematics of cultivation yields and contamination diagnostics using our free calculator tools at sporlyworks.com

#mushroomcultivation #mycologysociety #homebiology #spores #steriletechnique #mycelium #fungi #growblocks #sporlyworks""",

    "post3": """🛡️ DIETARY SUPPLEMENT PURITY: Beta-Glucans vs. Grain Starch

Not all mushroom supplements are created equal. 

Many retail brands sell 'mycelium on grain,' grinding the starchy substrate (rice or oats) into the product. This means you are paying for up to 70% starch. 

Clinical-grade supplements use 100% organic, hot-water extracted fruiting bodies to isolate pure, bioavailable beta-glucans. 

🌱 We partner with certified brands like FreshCap to provide verified active compound profiles. Read the purity guide at sporlyworks.com

#functionalmushrooms #adaptogens #reishi #cordyceps #lionsmane #freshcap #immunesupport #supplementpurity #sporlyworks"""
}

for name, text in captions.items():
    cap_path = os.path.join(DRAFTS_DIR, f"{name}.txt")
    with open(cap_path, "w") as f:
        f.write(text)
    print(f"Generated post caption: {cap_path}")
