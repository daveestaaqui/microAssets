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
    
    # Load Parchment Background or Cream
    parchment_path = os.path.join(BASE_DIR, "assets", "parchment-tile.jpg")
    if os.path.exists(parchment_path):
        tile = Image.open(parchment_path).convert("RGB")
        img = Image.new("RGB", (width, height))
        for x in range(0, width, tile.width):
            for y in range(0, height, tile.height):
                img.paste(tile, (x, y))
    else:
        img = Image.new("RGB", (width, height), "#FCFAF6")
        
    draw = ImageDraw.Draw(img)
    
    # Colors
    forest_green = "#0B4A2E"
    deep_green = "#143A27"
    gold = "#C59B27"
    earth_text = "#2C2418"
    
    # 1. Outer Elegant Borders
    draw.rectangle([30, 30, 1050, 1050], outline=forest_green, width=2)
    draw.rectangle([42, 42, 1038, 1038], outline=gold, width=1)
    
    # 2. Paste Clean Mushroom Emblem Logo (No embedded text in logo image)
    logo_placed = False
    logo_path = os.path.join(BASE_DIR, "assets", "logo-nav.png")
    if os.path.exists(logo_path):
        try:
            logo_img = Image.open(logo_path).convert("RGBA")
            # Target height 110px for clean elegant emblem header
            w, h = logo_img.size
            aspect = w / h
            target_h = 110
            target_w = int(target_h * aspect)
            logo_scaled = logo_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            logo_x = (width - target_w) // 2
            img.paste(logo_scaled, (logo_x, 50), logo_scaled)
            logo_placed = True
        except Exception as e:
            print(f"⚠️ Error pasting logo: {e}")
            
    # 3. Header Wordmark & Category Title
    header_y = 175 if logo_placed else 80
    header_font = get_font(FONT_SERIF_PATHS, 24)
    draw.text((width // 2, header_y), "SPORLYWORKS", fill=gold, font=header_font, anchor="mm")
    
    cat_y = header_y + 35
    cat_font = get_font(FONT_SANS_PATHS, 16)
    draw.text((width // 2, cat_y), title.upper()[:45], fill=forest_green, font=cat_font, anchor="mm")
    draw.line([(width // 2) - 80, cat_y + 18, (width // 2) + 80, cat_y + 18], fill=gold, width=1)
    
    # 4. Main Editorial Quote Text
    quote_font = get_font(FONT_SERIF_PATHS, 38)
    wrapped_lines = wrap_text(f"“{quote}”", quote_font, 840, draw)
    
    total_text_height = len(wrapped_lines) * 56
    content_center_y = 560
    start_y = content_center_y - (total_text_height // 2)
    
    for idx, line in enumerate(wrapped_lines):
        line_y = start_y + (idx * 56)
        draw.text((width // 2, line_y), line, fill=earth_text, font=quote_font, anchor="mm")
        
    # 5. Citation
    source_font = get_font(FONT_SANS_PATHS, 20)
    draw.text((width // 2, 860), f"Reference: {source}", fill=forest_green, font=source_font, anchor="mm")
    
    # 6. Footer
    footer_text = "SPORLYWORKS × MYCOLOGY & FUNCTIONAL WELLNESS"
    footer_font = get_font(FONT_SANS_PATHS, 16)
    draw.text((width // 2, 1000), footer_text, fill=gold, font=footer_font, anchor="mm")
    
    # Save Image
    img_path = os.path.join(DRAFTS_DIR, f"{output_name}.jpg")
    img.save(img_path, "JPEG", quality=98)
    print(f"Generated post image: {img_path}")

# Authentic, human, non-AI post captions
ENGAGING_TEMPLATES = {
    "lions-mane-neurogenesis": {
        "title": "Lion's Mane & Neural Regeneration: What the Research Shows",
        "caption": """Lion’s Mane (Hericium erinaceus) isn't magic—it’s biochemistry.

The mushroom contains two unique groups of active compounds: hericenones (found in the fruiting body) and erinacines (found in the mycelium).

Research shows these small molecules can cross the blood-brain barrier. Once inside, they stimulate Nerve Growth Factor (NGF)—a primary protein responsible for maintaining cholinergic neurons and building new synaptic connections.

What that means in practice:
• Steady cognitive focus without caffeine crash
• Support for long-term memory retention & neuroplasticity
• Natural nerve growth stimulation

If you take Lion's Mane, look for 100% organic hot-water extracted fruiting body powders with verified beta-glucan percentages (>25%), rather than products made from cheap grain fillers.

Read our full biochemical breakdown and try our interactive Wellness Stack Builder at sporlyworks.com

#mycology #lionsmane #nootropics #neurogenesis #functionalmushrooms #sporlyworks"""
    },
    "all-in-one-grow-bag-guide": {
        "title": "All-In-One Grow Bags: How to Avoid Contamination",
        "caption": """If you’ve ever lost a mushroom grow to Trichoderma, you know how frustrating it is.

The biggest point of failure in home mycology is during inoculation—exposing sterile grain or substrate to unsterile room air.

All-in-one grow bags solve this with two built-in safety mechanisms:
1. Self-healing injection ports that let you inject liquid culture without opening the bag.
2. 0.2-micron filter patches that allow gas exchange while blocking mold spores and bacteria.

Quick tip: When your bag hits about 30% colonization, break up the mycelium and shake the bag thoroughly. Mixing the colonized grain evenly into the substrate cuts your total fruiting time almost in half.

Calculate your substrate ratios and yield potential with our free calculators at sporlyworks.com

#mushroomgrowing #mycology #growbags #steriletechnique #homebiology #sporlyworks"""
    },
    "cordyceps-atp-cellular-energy": {
        "title": "Cordyceps & ATP Synthesis: Clean Endurance Science",
        "caption": """Unlike pre-workout stimulants that spike your central nervous system, Cordyceps militaris works at the cellular level.

Cordyceps contains cordycepin and adenosine—two nucleoside compounds that directly support ATP (adenosine triphosphate) synthesis in human cells.

Key physiological benefits:
• Increased oxygen uptake & VO2 kinetics
• Natural cellular ATP energy production
• Clean physical stamina without jitters or blood pressure spikes

Taking 1,000mg to 1,500mg about 45 minutes before exercise supports aerobic stamina naturally.

Read our full research breakdown at sporlyworks.com

#cordyceps #endurance #cellularhealth #functionalmushrooms #vo2max #sporlyworks"""
    },
    "identifying-grow-contamination": {
        "title": "How to Spot Trichoderma Before It Spreads",
        "caption": """The most common nightmare in cultivation is Trichoderma green mold.

Here’s how to catch it early:
• Dense, ultra-bright white growth that turns emerald green within 24 hours is Trichoderma sporulating.
• Light yellow liquid droplets on mycelium are just secondary metabolites ('myc piss')—a normal stress response, not mold.

Crucial rule: If you see green mold in a tub or bag, do NOT open it inside your grow space. Airborne spores will float across the room and contaminate future grows. Isolate the block immediately.

Use our free visual Contamination Diagnostic Guide at sporlyworks.com/tools/diagnostics.html

#mycology #growerrors #trichoderma #contamination #fungi #sporlyworks"""
    },
    "monotub-tek-beginners-guide": {
        "title": "The Standard CVG Substrate Formula",
        "caption": """Field capacity is the single most important parameter when preparing bulk mushroom substrate.

Too wet, and you risk sour rot. Too dry, and your mycelium stalls out before fruiting.

Standard CVG Substrate Recipe:
• 650g Coir Brick
• 2 Quarts Vermiculite
• 1 Cup Gypsum
• 3.5 to 4.0 Liters Boiling Water

Test field capacity: Take a handful of prepped substrate and squeeze hard. Only a few drops of water should squeeze out between your knuckles.

Use our free interactive CVG Substrate Calculator at sporlyworks.com/tools/substrate-calculator.html

#monotub #cvg #coir #substrateratio #mushroomcultivation #mycology #sporlyworks"""
    }
}

def generate_caption(title, keywords, slug, summary):
    custom = ENGAGING_TEMPLATES.get(slug)
    if custom:
        return custom["caption"]
        
    kw_tags = " ".join([f"#{k.strip().replace(' ', '').replace('-', '')}" for k in keywords.split(",") if k.strip()])
    return (
        f"{title}\n\n"
        f"{summary}\n\n"
        f"Read the complete research breakdown and use our free mycology tools at sporlyworks.com/blog/{slug}.html\n\n"
        f"{kw_tags} #sporlyworks #mycology #functionalmushrooms"
    )

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
            continue
            
        draw_post(
            title=title,
            quote=summary,
            source=f"sporlyworks.com/blog/{slug}",
            output_name=f"post_{slug}"
        )
        
        caption = generate_caption(title, keywords, slug, summary)
        cap_path = os.path.join(DRAFTS_DIR, f"post_{slug}.txt")
        with open(cap_path, "w", encoding="utf-8") as f:
            f.write(caption)
        print(f"Generated post caption: {cap_path}")

if __name__ == "__main__":
    main()
