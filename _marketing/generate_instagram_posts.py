#!/usr/bin/env python3
"""
SporlyWorks — High-Converting Instagram Parameter Card Generator
Architected by Astra (GPT-6 Astra) to maximize saves, shares, and authentic cultivator engagement.
Avoids generic AI summaries; produces screenshot-worthy parameter cards and field benchmarks.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS_DIR = os.path.join(BASE_DIR, "_marketing", "instagram_drafts")
os.makedirs(DRAFTS_DIR, exist_ok=True)

# Select Fonts
FONT_SERIF_PATHS = [
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
]
FONT_SANS_BOLD_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]
FONT_SANS_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]

def get_font(paths, size):
    for path in paths:
        if os.path.exists(path):
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

def draw_parameter_card(badge, title, parameters, footer_cta, output_name):
    width, height = 1080, 1080

    # 1. Base Canvas & Parchment Texture
    parchment_path = os.path.join(BASE_DIR, "assets", "parchment-tile.jpg")
    if not os.path.exists(parchment_path):
        parchment_path = os.path.join(BASE_DIR, "assets", "parchment-seamless.jpg")

    if os.path.exists(parchment_path):
        tile = Image.open(parchment_path).convert("RGB")
        img = Image.new("RGB", (width, height))
        for x in range(0, width, tile.width):
            for y in range(0, height, tile.height):
                img.paste(tile, (x, y))
    else:
        img = Image.new("RGB", (width, height), "#FCFAF6")

    draw = ImageDraw.Draw(img)

    # Palette
    forest_green = "#0B4A2E"
    deep_green = "#143A27"
    gold = "#C59B27"
    gold_dark = "#9E7B1B"
    earth_text = "#2C2418"
    card_bg = "#FFFFFF"
    card_border = "#0B4A2E"
    row_alt_bg = "#F7F5EE"
    alert_red = "#8B1E1E"

    # 2. Outer Architectural Borders
    draw.rectangle([24, 24, width - 24, height - 24], outline=forest_green, width=3)
    draw.rectangle([34, 34, width - 34, height - 34], outline=gold, width=1)

    # 3. Official Logo Emblem Header
    logo_path = os.path.join(BASE_DIR, "assets", "logo-nav.png")
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            target_h = 85
            aspect = logo.width / logo.height
            target_w = int(target_h * aspect)
            logo_scaled = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
            img.paste(logo_scaled, ((width - target_w) // 2, 48), logo_scaled)
        except Exception as e:
            print(f"Notice pasting logo: {e}")

    # 4. Brand Mark Wordmark
    brand_font = get_font(FONT_SERIF_PATHS, 20)
    draw.text((width // 2, 145), "SPORLYWORKS", fill=gold_dark, font=brand_font, anchor="mm")

    # 5. Category Badge Pill
    badge_font = get_font(FONT_SANS_BOLD_PATHS, 13)
    badge_text = badge.upper()
    b_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw = b_bbox[2] - b_bbox[0] + 28
    bh = 26
    bx1 = (width - bw) // 2
    by1 = 172
    draw.rounded_rectangle([bx1, by1, bx1 + bw, by1 + bh], radius=13, fill="#EFECE3", outline=gold, width=1)
    draw.text((width // 2, by1 + (bh // 2)), badge_text, fill=forest_green, font=badge_font, anchor="mm")

    # 6. Main Action Headline
    title_font = get_font(FONT_SERIF_PATHS, 32)
    t_lines = wrap_text(title, title_font, 920, draw)
    title_y = 230
    for line in t_lines:
        draw.text((width // 2, title_y), line, fill=earth_text, font=title_font, anchor="mm")
        title_y += 42

    # 7. Central Parameter Box (The High-Value Screenshot Card)
    card_x1 = 60
    card_x2 = width - 60
    card_y1 = max(title_y + 10, 290)
    card_y2 = 910
    card_height = card_y2 - card_y1

    # White/Cream high-contrast card background with subtle shadow
    draw.rounded_rectangle([card_x1 + 3, card_y1 + 4, card_x2 + 3, card_y2 + 4], radius=16, fill="#E2DDD0")
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=16, fill=card_bg, outline=card_border, width=2)

    # Render Parameter Rows
    num_rows = len(parameters)
    row_height = card_height / num_rows

    label_font = get_font(FONT_SANS_BOLD_PATHS, 15)
    val_font = get_font(FONT_SERIF_PATHS, 18)
    sub_font = get_font(FONT_SANS_PATHS, 14)

    for i, param in enumerate(parameters):
        ry1 = int(card_y1 + (i * row_height))
        ry2 = int(card_y1 + ((i + 1) * row_height))

        # Alternating subtle row tint
        if i % 2 == 1:
            draw.rectangle([card_x1 + 2, ry1, card_x2 - 2, ry2], fill=row_alt_bg)

        # Divider line
        if i > 0:
            draw.line([(card_x1 + 10), ry1, (card_x2 - 10), ry1], fill="#E5DFCE", width=1)

        # Row Content
        label = param.get("label", "").upper()
        value = param.get("value", "")
        note = param.get("note", "")
        is_alert = param.get("alert", False)

        tag_color = alert_red if is_alert else forest_green
        content_y = ry1 + int(row_height // 2)

        # Tag Badge
        draw.text((card_x1 + 35, content_y - 12), label, fill=tag_color, font=label_font, anchor="lm")
        # Value Text
        draw.text((card_x1 + 35, content_y + 12), value, fill=earth_text, font=val_font, anchor="lm")

        # Optional right-hand badge/note
        if note:
            draw.text((card_x2 - 35, content_y), note, fill=gold_dark, font=sub_font, anchor="rm")

    # 8. Footer Brand & Discovery Bar
    footer_y = 960
    draw.line([(width // 2) - 180, footer_y - 20, (width // 2) + 180, footer_y - 20], fill=gold, width=1)

    cta_font = get_font(FONT_SANS_BOLD_PATHS, 16)
    draw.text((width // 2, footer_y), footer_cta.upper(), fill=forest_green, font=cta_font, anchor="mm")

    sub_footer_font = get_font(FONT_SANS_PATHS, 13)
    draw.text((width // 2, footer_y + 26), "SAVE THIS PROTOCOL FOR LAB DAY • SPORLYWORKS.COM", fill=gold_dark, font=sub_footer_font, anchor="mm")

    # Save High-Resolution Image
    out_path = os.path.join(DRAFTS_DIR, f"{output_name}.jpg")
    img.save(out_path, "JPEG", quality=98)
    print(f"✅ Generated upgraded parameter card: {out_path}")
    return out_path

MASTER_POSTS = [
    {
        "id": "post1",
        "badge": "Cultivation Protocol • Substrate Hydration",
        "title": "Field Capacity: The 3-Drop Squeeze Rule",
        "parameters": [
            {
                "label": "Target Moisture",
                "value": "65% – 68% Substrate Hydration",
                "note": "Field Capacity Standard"
            },
            {
                "label": "The Hand Squeeze Test",
                "value": "Firm grip yields exactly 1 to 3 drops between knuckles",
                "note": "Optimal Benchmark"
            },
            {
                "label": "Over-Saturated (Streaming Water)",
                "value": "Anaerobic micro-pockets -> Trichoderma & sour rot",
                "note": "High Contam Risk",
                "alert": True
            },
            {
                "label": "Under-Saturated (Zero Drops)",
                "value": "Mycelium desiccates & stalls out before pinhead initiation",
                "note": "Yield Deficit"
            },
            {
                "label": "Coir Expansion Metric",
                "value": "1x Dry Coir Brick (650g) expands with ~3.25L Boiling Water",
                "note": "5:1 Ratio"
            }
        ],
        "footer_cta": "Calculate exact hydration for your tub -> sporlyworks.com",
        "caption": """Ever lost a monotub to green mold or sour rot? 90% of the time, the culprit isn't dirty genetics—it's over-saturated substrate.

When substrate is too wet, it suffocates the mycelial network. The lack of oxygen creates anaerobic micro-pockets where Trichoderma and bacterial blotch thrive before your mushroom mycelium can colonize.

Here is the exact field benchmark every veteran cultivator uses:
Grab a handful of pasteurized substrate and squeeze as hard as you can:
• Water streams out? ❌ Too wet. Add dry vermiculite immediately.
• Zero drops fall? ❌ Too dry. Your flush will stall before pins form.
• Exactly 1 to 3 drops between your knuckles? ✅ Perfect field capacity (65–68% hydration).

💡 Pro Tip: Standard coco coir bricks expand approximately 5x by weight. A standard 650g brick typically requires between 3.1L and 3.4L of boiling water.

What's your go-to substrate recipe? Straight coir, or CVG (Coir/Verm/Gypsum)? Drop your mix below 🧪👇

Save this protocol card to your collection for your next substrate prep day.

Need exact water measurements for your custom tub size? Use our free interactive Substrate Hydration Calculator at sporlyworks.com (link in bio).

#mushroomcultivation #mycologysociety #homebiology #growblocks #monotubtek #spores #steriletechnique #mycelium #sporlyworks"""
    },
    {
        "id": "post2",
        "badge": "Biochemistry • Functional Extraction",
        "title": "Hot Water vs Alcohol: The Dual-Extract Trap",
        "parameters": [
            {
                "label": "Hot Water Extraction",
                "value": "Fractures chitin walls to release Beta-1,3/1,6-D-Glucans",
                "note": "Immunomodulation"
            },
            {
                "label": "Ethanol Alcohol Extraction",
                "value": "Dissolves non-polar Triterpenes, Hericenones & Sterols",
                "note": "Neurogenesis"
            },
            {
                "label": "The Commercial Trap",
                "value": "Grain-grown mycelium with 50%+ unfermented starch fillers",
                "note": "Zero Efficacy",
                "alert": True
            },
            {
                "label": "Verified Lab Benchmark",
                "value": ">25% Verified Beta-Glucans from 100% Pure Fruiting Body",
                "note": "Gold Standard"
            },
            {
                "label": "Mushroom Synergy",
                "value": "Lion's Mane: Fruiting body + mycelium | Reishi: Dual extract required",
                "note": "Species Specific"
            }
        ],
        "footer_cta": "Explore active extraction science -> sporlyworks.com",
        "caption": """Most commercial "dual-extract" mushroom supplements on the market are cutting corners.

Here is the underlying biochemistry:

1. Hot Water Extraction:
Fungal cell walls are made of indigestible chitin. High-temperature water decoction is required to fracture the chitinous matrix and release water-soluble Beta-1,3/1,6-D-Glucans—the primary compounds responsible for immune modulation and macrophage activation.

2. Ethanol (Alcohol) Extraction:
Non-polar bioactive compounds like Triterpenes (in Reishi) and Hericenones (in Lion’s Mane) are practically insoluble in water. They require pure grain alcohol soaking to dissolve and concentrate.

The Trap? Many brands take cheap mycelium grown on oats or rice, grind up the starch filler, and label it "dual extract" without verifying active compound percentages.

Look for 100% organic fruiting bodies with third-party tested beta-glucan percentages (>25%), not total polysaccharide counts padded by grain starch.

Do you brew your own mushroom tinctures or buy dual extracts? Share your setup below 🍄

Check out our full extraction protocols and interactive wellness stacks at sporlyworks.com

#functionalmushrooms #nootropics #lionsmane #reishi #cordyceps #adaptogens #biohacking #neurogenesis #sporlyworks"""
    },
    {
        "id": "post3",
        "badge": "Laboratory Protocol • Genetics Isolation",
        "title": "Agar vs Liquid Culture: The Isolator's Guide",
        "parameters": [
            {
                "label": "Stage 1: Spore to Agar (2% MEA)",
                "value": "Germinate and sector ropey rhizomorphic growth away from bacteria",
                "note": "Genetic Cleaning"
            },
            {
                "label": "Stage 2: Agar to Liquid Culture (4% LME)",
                "value": "Rapid 14-day 500mL expansion of verified monoculture",
                "note": "Rapid Inoculation"
            },
            {
                "label": "Direct Spore to Grain Inoculation",
                "value": "High bacterial risk & multi-strain genetic competition",
                "note": "Avoid in Production",
                "alert": True
            },
            {
                "label": "Storage Benchmark",
                "value": "Liquid Culture: 6–9 months at 38°F (4°C) in sealed borosilicate",
                "note": "Cold Vault"
            },
            {
                "label": "Contamination Detection",
                "value": "Cloudy/turbid broth = Bacteria | Clean clear broth = Healthy mycelium",
                "note": "Visual QC"
            }
        ],
        "footer_cta": "Master sterile laboratory technique -> sporlyworks.com",
        "caption": """Stop injecting multi-spore syringes directly into grain bags.

A single spore syringe contains millions of competing genetic pairings—plus whatever microscopic airborne bacteria hitched a ride during spore printing. Inoculating grain directly is rolling the dice.

Here is the clean two-stage protocol:

Step 1: Spore to Agar (2% Malt Extract Agar)
Germinate your spores on petri dishes. As mycelium expands, identify the fastest, ropey rhizomorphic growth. Take a sterile 2mm scalpel transfer from the outer leading edge to a fresh plate. You now have clean, sector-isolated genetics with zero bacterial load.

Step 2: Clean Agar to Liquid Culture (4% LME Broth)
Drop a clean colonized agar wedge into sterile malt extract broth. Within 10–14 days, you have 500mL of high-potency liquid mycelium ready to inoculate dozens of grain jars in record time.

Are you team Agar plates or team Liquid Culture? Drop your vote below 👇

Save this isolation protocol for your next laboratory session.

Calculate your exact malt and dextrose broth measurements with our free tools at sporlyworks.com

#mycology #steriletechnique #agar #liquidculture #spores #fungi #mushroomgrower #labprotocols #sporlyworks"""
    }
]

def generate_all_posts():
    print("🎨 Generating upgraded Astra-designed Instagram Parameter Cards...")
    for post in MASTER_POSTS:
        # 1. Render Graphic
        draw_parameter_card(
            badge=post["badge"],
            title=post["title"],
            parameters=post["parameters"],
            footer_cta=post["footer_cta"],
            output_name=post["id"]
        )
        # 2. Write Caption
        cap_path = os.path.join(DRAFTS_DIR, f"{post['id']}.txt")
        with open(cap_path, "w", encoding="utf-8") as f:
            f.write(post["caption"])
        print(f"📝 Wrote caption for {post['id']}: {cap_path}")

    print("🎉 All upgraded Instagram posts compiled successfully!")

if __name__ == "__main__":
    generate_all_posts()
