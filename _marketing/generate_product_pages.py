#!/usr/bin/env python3
import os
import json

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
PRODUCTS_DIR = os.path.join(BASE_DIR, "products")
os.makedirs(PRODUCTS_DIR, exist_ok=True)

STYLE_PATH = "../style.css?v=602"
FAVICON_PATH = "../assets/favicon.ico"
NAV_ICON = "../assets/icon-128.png"

PRODUCT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — SporlyWorks Science-Backed Products</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <link rel="canonical" href="https://sporlyworks.com/products/{slug}.html">
    <link rel="icon" type="image/x-icon" href="{favicon}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Serif+Display&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{style_path}">
    <style>
        .product-page-body {{
            max-width: 1000px;
            margin: 120px auto 80px;
            padding: 0 24px;
        }}
        .product-header {{
            display: flex;
            flex-direction: column;
            md-flex-direction: row;
            gap: 48px;
            margin-bottom: 60px;
            align-items: center;
        }}
        @media (min-width: 768px) {{
            .product-header {{
                flex-direction: row;
            }}
        }}
        .product-img-wrapper {{
            flex: 1;
            max-width: 400px;
            background: var(--bg-surface-elevated);
            padding: 24px;
            border-radius: var(--radius-md);
            border: 1px solid var(--glass-border);
            box-shadow: var(--shadow-soft);
        }}
        .product-img-wrapper img {{
            width: 100%;
            height: auto;
            object-fit: contain;
            border-radius: var(--radius-sm);
        }}
        .product-details {{
            flex: 1.2;
        }}
        .product-cat {{
            color: var(--gold-dark);
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .product-name {{
            font-size: 38px;
            color: var(--green-dark);
            margin-bottom: 12px;
            line-height: 1.2;
            font-family: 'DM Serif Display', Georgia, serif;
        }}
        .product-tagline {{
            font-size: 18px;
            color: var(--text-secondary);
            font-style: italic;
            margin-bottom: 24px;
        }}
        .product-features-list {{
            margin-bottom: 32px;
            list-style: none;
            padding: 0;
        }}
        .product-features-list li {{
            margin-bottom: 12px;
            font-size: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-primary);
        }}
        .product-features-list li::before {{
            content: '✓';
            color: var(--green-light);
            font-weight: 800;
        }}
        .product-cta-btn {{
            display: inline-block;
            background: linear-gradient(135deg, var(--green-light), var(--green));
            color: white;
            padding: 14px 36px;
            border-radius: var(--radius-pill);
            text-decoration: none;
            font-weight: 700;
            font-size: 16px;
            transition: all 0.3s;
            box-shadow: 0 4px 14px rgba(11, 74, 46, 0.2);
        }}
        .product-cta-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(11, 74, 46, 0.3);
        }}
        .science-section {{
            background: var(--bg-surface-elevated);
            padding: 40px;
            border-radius: var(--radius-md);
            border: 1px solid var(--glass-border);
            margin-bottom: 48px;
            box-shadow: var(--shadow-soft);
        }}
        .science-section h3 {{
            color: var(--green);
            font-size: 24px;
            margin-bottom: 16px;
            font-family: 'DM Serif Display', Georgia, serif;
        }}
        .science-section p {{
            font-size: 15px;
            line-height: 1.7;
            color: var(--text-secondary);
            margin-bottom: 16px;
        }}
        .science-ref {{
            font-size: 12px;
            color: var(--text-muted);
            font-style: italic;
            border-top: 1px solid var(--glass-border);
            padding-top: 12px;
            margin-top: 16px;
        }}
        .usage-section h3 {{
            color: var(--green-dark);
            font-size: 24px;
            margin-bottom: 16px;
            font-family: 'DM Serif Display', Georgia, serif;
        }}
        .usage-section p {{
            font-size: 15px;
            line-height: 1.7;
            color: var(--text-primary);
            margin-bottom: 24px;
        }}
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            text-decoration: none;
            color: var(--green-light);
            font-weight: 600;
            margin-bottom: 32px;
            transition: transform 0.2s;
        }}
        .back-link:hover {{
            transform: translateX(-4px);
        }}
        .fda-disclaimer {{
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.5;
            background: #ffffff;
            padding: 16px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--glass-border);
            margin-top: 60px;
        }}
    </style>
</head>
<body>

    <!-- ═══ NAVIGATION ═══ -->
    <nav id="mainNav" class="scrolled">
        <div class="nav-inner">
            <a href="../index.html" class="nav-brand">
                <img src="{nav_icon}" alt="SporlyWorks" class="nav-icon" style="height:60px; width:60px;">
                <span class="nav-wordmark" style="font-size:24px;">SPORLYWORKS</span>
            </a>
            <div class="nav-links">
                <a href="../index.html#genetics">Cultivation</a>
                <a href="../index.html#supplements">Supplements</a>
                <a href="../index.html#research">Science</a>
            </div>
            <a href="../index.html#genetics" class="nav-cta" style="background:linear-gradient(135deg, var(--green-light), var(--green)); color:white; padding:10px 24px; border-radius:99px; text-decoration:none; font-weight:600;">Shop Collection</a>
        </div>
    </nav>

    <!-- ═══ MAIN CONTENT ═══ -->
    <main class="product-page-body">
        <a href="../index.html" class="back-link">← Back to Home</a>
        
        <section class="product-header">
            <div class="product-img-wrapper">
                <img src="{image_url}" alt="{product_name}">
            </div>
            <div class="product-details">
                <div class="product-cat">{category}</div>
                <h1 class="product-name">{product_name}</h1>
                <p class="product-tagline">{tagline}</p>
                <ul class="product-features-list">
                    {features_html}
                </ul>
                <a href="{partner_url}" id="cta-{partner_key}" class="product-cta-btn" target="_blank" rel="noopener">{cta_label}</a>
            </div>
        </section>

        <section class="science-section">
            <h3>🔬 Scientific Clinical Backing</h3>
            {science_html}
            <div class="science-ref">{science_citation}</div>
        </section>

        <section class="usage-section">
            <h3>📦 Dosage & Application</h3>
            {usage_html}
        </section>

        <div class="fda-disclaimer">
            <strong>FDA & Legal Disclaimer:</strong> {disclaimer}
        </div>
    </main>

    <!-- ═══ FOOTER ═══ -->
    <footer style="padding: 80px 24px 40px; background: var(--green-dark); color: var(--text-on-dark); border-top: 1px solid var(--glass-border); text-align: center; margin-top: 80px;">
        <div class="container">
            <a href="../index.html" style="display:inline-flex; align-items:center; gap:12px; text-decoration:none; font-family:'DM Serif Display',serif; color:var(--gold-light); font-size:24px; margin-bottom:24px;">
                <img src="{nav_icon}" alt="SporlyWorks" style="height:32px; width:32px;">
                <span style="color:var(--gold-light); letter-spacing:3px;">SPORLYWORKS</span>
            </a>
            <div style="display:flex; justify-content:center; gap:32px; margin-bottom:32px;">
                <a href="../index.html#genetics" style="color:var(--text-on-dark); text-decoration:none; opacity:0.8;">Cultivation</a>
                <a href="../index.html#supplements" style="color:var(--text-on-dark); text-decoration:none; opacity:0.8;">Supplements</a>
                <a href="../privacy.html" style="color:var(--text-on-dark); text-decoration:none; opacity:0.8;">Privacy Policy</a>
            </div>
            <p style="color:var(--text-on-dark); opacity:0.6; font-size:12px; max-width:600px; margin:0 auto 12px;">Affiliate Disclosure: We may earn a referral commission when you make a purchase through our partner links at no additional cost to you.</p>
            <p style="color:var(--text-on-dark); opacity:0.6; font-size:11px;">&copy; 2026 SporlyWorks. All rights reserved.</p>
        </div>
    </footer>

    <script>
    fetch('../affiliate_config.json')
        .then(r => r.json())
        .then(config => {{
            const partner = config.partners['{partner_key}'];
            if (partner) {{
                let url = partner.base_url;
                const isPlaceholder = !partner.affiliate_id || 
                                      partner.affiliate_id.startsWith('YOUR_') || 
                                      partner.affiliate_id.includes('INSERT');
                if (!isPlaceholder) {{
                    url = partner.affiliate_url_template.replace('{{affiliate_id}}', partner.affiliate_id);
                }}
                const btn = document.getElementById('cta-{partner_key}');
                if (btn) btn.href = url;
            }}
        }})
        .catch(() => console.log('Config fetch skipped - using default links'));
    </script>
</body>
</html>
"""

products = [
    {
        "slug": "lions-mane-extract",
        "title": "Real Mushrooms Lion's Mane Extract Powder",
        "category": "Supplements",
        "product_name": "Organic Lion's Mane Extract Powder",
        "tagline": "Cognitive Clarity, Memory Support & Nerve Growth Factor (NGF) Stimulation",
        "image_url": "../assets/real_images/real_mushrooms.png",
        "partner_key": "real_mushrooms",
        "partner_url": "https://www.realmushrooms.com",
        "cta_label": "Shop Lion's Mane at Real Mushrooms →",
        "features_html": """
            <li>100% Organic Lion's Mane Mushroom (Hericium erinaceus)</li>
            <li>Hot-water extracted from 100% organic fruiting bodies</li>
            <li>Verified Beta-glucans (>25%), No added starch, grains, or fillers</li>
            <li>Gluten-free, Non-GMO, Vegan, and USDA Certified Organic</li>
        """,
        "science_html": """
            <p>Lion's Mane is unique in its ability to support brain health. It contains key active compounds (hericenones and erinacines) that stimulate the synthesis of Nerve Growth Factor (NGF). NGF is a protein crucial for the development, function, and survival of brain cells.</p>
            <p>Clinical research supports its use for mild cognitive impairment, showing statistically significant improvements in cognitive test scores in double-blind, placebo-controlled trials after 8 to 16 weeks of consistent daily usage.</p>
        """,
        "science_citation": "Clinical Study Reference: Mori, K., et al. (2009). Phytotherapy Research, 23(3), 367-372. 'Improving effects of the mushroom Yamabushitake (Hericium erinaceus) on mild cognitive impairment.'",
        "usage_html": """
            <p>Take 1,000 mg (approx. 1/2 teaspoon) daily. Easily dissolves into hot water, morning coffee, herbal teas, or protein shakes. For maximum bioavailability, consume alongside a fat source or warm liquid.</p>
        """,
        "disclaimer": "These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease. Regular health check-ups and consulting a medical professional are recommended before starting any new supplement.",
        "keywords": "lions mane powder, organic mushroom extract, NGF brain supplement, cognitive health, real mushrooms lions mane"
    },
    {
        "slug": "cordyceps-extract",
        "title": "Real Mushrooms Cordyceps Extract Powder",
        "category": "Supplements",
        "product_name": "Organic Cordyceps Militaris Extract Powder",
        "tagline": "Cellular Energy, ATP Production & Cardiovascular Endurance",
        "image_url": "../assets/real_images/real_mushrooms.png",
        "partner_key": "real_mushrooms",
        "partner_url": "https://www.realmushrooms.com",
        "cta_label": "Shop Cordyceps at Real Mushrooms →",
        "features_html": """
            <li>100% Organic Cordyceps Militaris Mushroom</li>
            <li>Hot-water extracted from 100% organic fruiting bodies</li>
            <li>Verified Beta-glucans (>20%) and Cordycepin (>0.3%)</li>
            <li>No added grain, starch, mycelium, or fillers</li>
        """,
        "science_html": """
            <p>Cordyceps has been prized for centuries as an adaptogen that increases energy and stamina. Modern clinical trials support its ability to improve VO2 max (maximum oxygen intake) and extend the time to exhaustion during high-intensity exercise by optimizing cellular oxygen kinetics and respiratory exchange ratios.</p>
            <p>Unlike synthetic stimulants, Cordyceps supports energy organically by enhancing the body's synthesis of adenosine triphosphate (ATP), the primary energy currency of cells.</p>
        """,
        "science_citation": "Clinical Study Reference: Hirsch, K. R., et al. (2017). Journal of Dietary Supplements, 14(1), 42-53. 'Cordyceps militaris improves tolerance to high-intensity exercise after acute and chronic supplementation.'",
        "usage_html": """
            <p>Take 1,000 mg (approx. 1/2 teaspoon) daily. Cordyceps has a mildly sweet, earthy taste that pairs perfectly with pre-workout beverages, green smoothies, or black tea. Best taken in the morning or early afternoon for sustained daily energy.</p>
        """,
        "disclaimer": "These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease. Consult your physician if you are pregnant, nursing, or taking blood thinners.",
        "keywords": "cordyceps powder, energy supplement, ATP oxygen endurance, real mushrooms cordyceps, adaptogen energy"
    },
    {
        "slug": "reishi-extract",
        "title": "Real Mushrooms Reishi Extract Powder",
        "category": "Supplements",
        "product_name": "Organic Reishi Mushroom Extract Powder",
        "tagline": "Stress Resilience, Calming Support & Immune Modulation",
        "image_url": "../assets/real_images/real_mushrooms.png",
        "partner_key": "real_mushrooms",
        "partner_url": "https://www.realmushrooms.com",
        "cta_label": "Shop Reishi at Real Mushrooms →",
        "features_html": """
            <li>100% Organic Red Reishi Mushroom (Ganoderma lingzhi)</li>
            <li>Dual-extracted (water + alcohol) to isolate both water-soluble beta-glucans and fat-soluble triterpenes</li>
            <li>Verified Beta-glucans (>15%) and Triterpenes (>4%)</li>
            <li>Certified organic, USDA organic, gluten-free, vegan</li>
        """,
        "science_html": """
            <p>Reishi is known as the 'mushroom of immortality' and is highly regarded as a potent adaptogen. Research indicates that Reishi's bioactive compounds, particularly triterpenes and polysaccharides, modulate the immune response and help support the central nervous system during physical and mental stress.</p>
            <p>Triterpenes interact with GABA pathways in the brain to encourage calm, relaxation, and deeper restorative sleep cycles.</p>
        """,
        "science_citation": "Clinical Study Reference: Wachtel-Galor, S., et al. (2011). Herbal Medicine: Biomolecular and Clinical Aspects. 2nd edition. Chapter 9: 'Ganoderma lucidum (Reishi/Lingzhi): Science-backed adaptogenic profiles.'",
        "usage_html": """
            <p>Take 1,000 mg (approx. 1/2 teaspoon) daily. Reishi is naturally bitter due to the therapeutic triterpenes. We recommend mixing it into dark cocoa, coffee, warm nut milks, or capping it to bypass the bitter flavor profiles. Best consumed in the evening.</p>
        """,
        "disclaimer": "These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease. Please consult with your physician before combining with immune-suppressants.",
        "keywords": "reishi powder, stress adaptogen, calm sleep supplement, real mushrooms reishi, organic ganoderma extract"
    },
    {
        "slug": "seed-ds01",
        "title": "Seed DS-01® Daily Synbiotic",
        "category": "Probiotics",
        "product_name": "DS-01® Daily Synbiotic (Probiotic + Prebiotic)",
        "tagline": "Systemic Health, Gastrointestinal Survivability & Gut Microbiome Balance",
        "image_url": "../assets/real_images/seed_ds01.png",
        "partner_key": "seed",
        "partner_url": "https://seed.com",
        "cta_label": "Shop DS-01 at Seed Probiotics →",
        "features_html": """
            <li>24 clinically and scientifically studied probiotic strains</li>
            <li>ViaCap® delivery system: dual-chamber capsule protects live strains against digestion</li>
            <li>Non-fermenting prebiotic outer capsule sourced from Indian pomegranate</li>
            <li>Free from gluten, dairy, soy, corn, binders, or preservatives</li>
        """,
        "science_html": """
            <p>Seed's DS-01® is validated using in vitro SHIME® (Simulator of the Human Intestinal Microbial Ecosystem) digestive testing. Results confirm that the nested dual-capsule preserves the live bacteria through the harsh acidic environment of the stomach and duodenum, delivering 100% of the active dose to the lower bowel and colon.</p>
            <p>Strains in DS-01 are clinically shown to support gastrointestinal function, intestinal barrier integrity, skin health, heart health, and natural folate synthesis.</p>
        """,
        "science_citation": "Clinical & Lab Reference: Seed Health Scientific Advisory Board (2020-2025). Clinical trials and SHIME simulation outputs for the ViaCap multi-chamber capsule.",
        "usage_html": """
            <p>Take 2 capsules daily, preferably all at once on an empty stomach to limit exposure to digestive enzymes. Start with 1 capsule daily for the first 3 days to allow your gut microbiome to adjust, then increase to the full 2-capsule daily dose.</p>
        """,
        "disclaimer": "These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease. Store in a cool, dry place. No refrigeration required.",
        "keywords": "seed probiotic, ds01 synbiotic, gut microbiome health, gut barrier integrity, dual capsule probiotic"
    },
    {
        "slug": "gourmet-grow-kits",
        "title": "North Spore Gourmet Mushroom Grow Kits",
        "category": "Cultivation",
        "product_name": "Gourmet Mushroom Grow Kits",
        "tagline": "100% Guaranteed-to-Grow Pre-Colonized Mushroom Blocks",
        "image_url": "../assets/illustrations/northspore.png",
        "partner_key": "north_spore",
        "partner_url": "https://northspore.com",
        "cta_label": "Shop Grow Kits at North Spore →",
        "features_html": """
            <li>Pre-colonized organic oak-sawdust fruiting block</li>
            <li>Harvest gourmet mushrooms at home in just 10-14 days</li>
            <li>Guaranteed to grow: North Spore replaces any block that fails</li>
            <li>Species options: Blue Oyster, Lion's Mane, Golden Oyster, Pink Oyster</li>
        """,
        "science_html": """
            <p>Mushroom grow kits capitalize on Biological Efficiency (BE). North Spore pre-colonizes their blocks in professional cleanrooms with laminar HEPA flow hoods. This allows the target mycelium to completely saturate the substrate (supplemented oak sawdust) without competing pathogens.</p>
            <p>By the time the kit arrives, the block is primed to fruit immediately upon exposure to humidity and fresh air. This bypasses the highly sensitive, sterile-critical stages of liquid culture inoculation and spawn run.</p>
        """,
        "science_citation": "Mycology Reference: Stamets, P. (2000). Growing Gourmet and Medicinal Mushrooms. Ten Speed Press. 'Biological efficiency ratios in wood-decaying saprophytes.'",
        "usage_html": """
            <p>Slice a 2-inch 'X' or slit on the side of the plastic bag. Spray the cut area 2-3 times daily with the included misting bottle. Keep in a room with indirect light and ambient temperatures between 60°F and 75°F. Harvest your crop once the caps begin to flatten out.</p>
        """,
        "disclaimer": "Cultivation Block for culinary and medicinal gourmet species. Always wash hands before handling substrate and ensure adequate ventilation in your fruiting environment. Check your local regulations regarding mushroom cultivation.",
        "keywords": "north spore grow kit, oyster mushroom kit, grow mushrooms at home, colonized substrate block, mycology kit"
    }
]

for prod in products:
    html = PRODUCT_TEMPLATE.format(
        title=prod["title"],
        description=prod["tagline"],
        keywords=prod["keywords"],
        slug=prod["slug"],
        favicon=FAVICON_PATH,
        style_path=STYLE_PATH,
        nav_icon=NAV_ICON,
        image_url=prod["image_url"],
        category=prod["category"],
        product_name=prod["product_name"],
        tagline=prod["tagline"],
        features_html=prod["features_html"].strip(),
        partner_url=prod["partner_url"],
        partner_key=prod["partner_key"],
        cta_label=prod["cta_label"],
        science_html=prod["science_html"].strip(),
        science_citation=prod["science_citation"],
        usage_html=prod["usage_html"].strip(),
        disclaimer=prod["disclaimer"]
    )
    
    file_path = os.path.join(PRODUCTS_DIR, f"{prod['slug']}.html")
    with open(file_path, "w") as f:
        f.write(html)
    print(f"Generated Product Page: {file_path}")

print("🎉 Product Page Generation Complete! Generated 5 product pages under /products/")
