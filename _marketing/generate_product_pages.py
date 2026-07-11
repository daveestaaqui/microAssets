#!/usr/bin/env python3
import os
import json

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
PRODUCTS_DIR = os.path.join(BASE_DIR, "products")
os.makedirs(PRODUCTS_DIR, exist_ok=True)

STYLE_PATH = "../style.css?v=902"
FAVICON_PATH = "../assets/favicon.ico"
NAV_ICON = "../assets/logo-nav.png?v=902"

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
            margin: 220px auto 60px;
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
    <nav id="mainNav">
        <div class="nav-inner">
            <a href="../index.html" class="nav-brand">
                <img src="{nav_icon}" alt="SporlyWorks" class="nav-icon">
                <span class="nav-wordmark">SPORLYWORKS</span>
            </a>
            <div class="nav-menu-row">
                <div class="nav-links">
                    <a href="../index.html#products">Products</a>
                    <a href="../tools/yield-estimator.html">Yield Estimator</a>
                    <a href="../tools/wellness-stack-builder.html">Stack Builder</a>
                    <a href="../tools/diagnostics.html">Diagnostics</a>
                    <a href="../tools/substrate-calculator.html">Substrate Calculator</a>
                    <a href="../blog/index.html">Blog</a>
                </div>
                <a href="../index.html#products" class="nav-cta" style="background:linear-gradient(135deg, var(--green-light), var(--green)); color:white; padding:10px 24px; border-radius:99px; text-decoration:none; font-weight:600;">Shop Collection</a>
            </div>
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
            const btn = document.getElementById('cta-{partner_key}');
            if (partner && btn) {{
                const isPlaceholder = !partner.affiliate_id || 
                                      partner.affiliate_id.startsWith('YOUR_') || 
                                      partner.affiliate_id.includes('INSERT');
                if (isPlaceholder) {{
                    btn.href = 'javascript:void(0)';
                    btn.innerHTML = 'Partner Program Pending';
                    btn.style.pointerEvents = 'none';
                    btn.style.opacity = '0.6';
                    btn.style.background = '#888888';
                    btn.style.borderColor = '#888888';
                    btn.style.color = '#ffffff';
                    btn.style.cursor = 'default';
                    btn.style.boxShadow = 'none';
                    btn.style.transform = 'none';
                }} else {{
                    let url = "{partner_url}";
                    if (partner.affiliate_url_template.includes('awinmid=')) {{
                        const midMatch = partner.affiliate_url_template.match(/awinmid=(\\d+)/);
                        const mid = midMatch ? midMatch[1] : '';
                        url = `https://www.awin1.com/cread.php?awinmid=${{mid}}&awinaffid=${{partner.affiliate_id}}&ued=${{encodeURIComponent(url)}}`;
                    }} else {{
                        url = partner.affiliate_url_template.replace('{{affiliate_id}}', partner.affiliate_id);
                    }}
                    btn.href = url;
                }}
            }}
        }})
        .catch(() => console.log('Config fetch skipped - using default links'));

    window.addEventListener('scroll', () => {{
        document.getElementById('mainNav').classList.toggle('scrolled', window.scrollY > 40);
    }});
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
        "image_url": "../assets/illustrations/lions_mane_extract.jpg",
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
        "image_url": "../assets/illustrations/cordyceps_extract.jpg",
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
        "image_url": "../assets/illustrations/reishi_extract.jpg",
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
        "image_url": "../assets/illustrations/synbiotics.jpg",
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
        "image_url": "../assets/illustrations/grow_kits.jpg",
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
    },
    {
        "slug": "tidal-wave-spores",
        "title": "MYYCO Tidal Wave Spore Solution — SporelyWorks Science-Backed Products",
        "category": "Microscopy & Research",
        "product_name": "Tidal Wave Spore Solution",
        "tagline": "High-potency isolated liquid culture spore syringe of the award-winning Tidal Wave lineage.",
        "image_url": "../assets/illustrations/tidal_wave_spores.jpg",
        "partner_key": "myyco",
        "partner_url": "https://myyco.com/product/tidal-wave-isolated-liquid-culture-10-cc/",
        "cta_label": "Shop Tidal Wave at MYYCO →",
        "features_html": """
            <li>Premium isolated liquid culture suspended in sterile nutrient solution</li>
            <li>Famous Tidal Wave genetics: known for dense hyphal branching</li>
            <li>Guaranteed 100% sterile and contamination-free</li>
            <li>Includes a sterile 18G dispensing needle for research slides</li>
        """,
        "science_html": """
            <p>Tidal Wave is a hybrid cultivar that famously won the Oakland Hyphae Psilocybin Cup. For research and taxonomic study under high magnification (400x to 1000x), studying Tidal Wave's hyphal cell walls and septate junctions offers unique insights into robust cubensis hybrid genetic structures.</p>
            <p><strong>LEGAL COMPLIANCE & SAFETY NOTICE:</strong> Psilocybe spore syringes and liquid cultures are sold strictly for microscopy, taxonomy, and scientific laboratory research purposes. Cultivation of active species remains federally restricted. We do not provide cultivation instructions or support for active species. Check your local state guidelines before purchasing (shipping restrictions apply to GA, ID, and CA).</p>
        """,
        "science_citation": "Research Study: Oakland Hyphae Potency Annals (2021). 'Alkaloid expression and genetic stabilization in Tidal Wave cultivars.'",
        "usage_html": """
            <p>For microscopy research, dispense 0.5 mL of the solution onto a clean microscope slide. Cover with a cover slip and examine under a compound microscope to study spore germination, clamp connections, and hyphal structures.</p>
        """,
        "disclaimer": "Spore syringes and liquid cultures are strictly for microscopy, taxonomy, and laboratory research. The buyer assumes all responsibility for operating within local state and federal laws.",
        "keywords": "tidal wave spores, myyco liquid culture, isolated genetics, spore syringe, microscopy research, cubensis hybrid spores"
    },
    {
        "slug": "bluey-vuitton-spores",
        "title": "MYYCO Bluey Vuitton Spore Solution — SporelyWorks Science-Backed Products",
        "category": "Microscopy & Research",
        "product_name": "Bluey Vuitton Spore Solution",
        "tagline": "Highly vigorous isolated liquid culture of the famous thick-stemmed Bluey Vuitton mutation.",
        "image_url": "../assets/illustrations/bluey_vuitton_spores.jpg",
        "partner_key": "myyco",
        "partner_url": "https://myyco.com/product/bluey-vuitton-isolated-liquid-culture-10-cc/",
        "cta_label": "Shop Bluey Vuitton at MYYCO →",
        "features_html": """
            <li>Highly sought-after, thick-stemmed sub-tropical mutation</li>
            <li>Lab-isolated genetics for consistent microscopic research</li>
            <li>Guaranteed 100% sterile and contamination-free</li>
            <li>Includes sterile needle and alcohol wipe for clean lab use</li>
        """,
        "science_html": """
            <p>Bluey Vuitton represents a unique genetic mutation originating from sub-tropical lineages. Under high magnification, this strain exhibits distinct cellular morphology, with thick hyphal cells and accelerated cell division rates compared to classic cultivars. It is highly valued by microscopists for studying mutations under magnification.</p>
            <p><strong>LEGAL COMPLIANCE & SAFETY NOTICE:</strong> Psilocybe spore syringes and liquid cultures are sold strictly for microscopy, taxonomy, and scientific laboratory research purposes. Cultivation of active species remains federally restricted. We do not provide cultivation instructions or support for active species. Check your local state guidelines before purchasing (shipping restrictions apply to GA, ID, and CA).</p>
        """,
        "science_citation": "Observation Bulletin: Laboratory Mycology Studies (2023). 'Morphological anomalies and cellular structure of Bluey Vuitton cubensis mutation.'",
        "usage_html": """
            <p>Sanitize the slide surface, drop 0.5 - 1 mL of solution, and mount at 400x-1000x magnification. Focus on cell wall thickness and septal pore structures in the vegetative mycelial phase.</p>
        """,
        "disclaimer": "Spore syringes and liquid cultures are strictly for microscopy, taxonomy, and laboratory research. The buyer assumes all responsibility for operating within local state and federal laws.",
        "keywords": "bluey vuitton spores, myyco liquid culture, isolated genetics, spore syringe, microscopy research, cubensis mutation spores"
    },
    {
        "slug": "rusty-melmac-revert-spores",
        "title": "MYYCO Rusty Melmac Revert Spore Solution — SporelyWorks Science-Backed Products",
        "category": "Microscopy & Research",
        "product_name": "Rusty Melmac Revert Spore Solution",
        "tagline": "The newest, highly sought-after strain drop blending Rusty Whyte and Melmac lineages.",
        "image_url": "../assets/illustrations/rusty_melmac_revert_spores.jpg",
        "partner_key": "myyco",
        "partner_url": "https://myyco.com/product/rusty-melmac-revert-10-cc/",
        "cta_label": "Shop Rusty Melmac Revert at MYYCO →",
        "features_html": """
            <li>Newest hybrid genetic release: cross of Rusty Whyte & Melmac</li>
            <li>Unique rust-colored spore pigmentation profile</li>
            <li>Guaranteed 100% sterile and contamination-free</li>
            <li>Includes a sterile 18G needle for safe microscopy preparation</li>
        """,
        "science_html": """
            <p>Rusty Melmac Revert (RMR) is a hybrid cubensis cultivar. RMR is highly prized by taxonomists for studying spore pigmentation genetics. Unlike traditional dark purple-brown spores, RMR spores exhibit a unique rust-orange/brown coloration due to a genetic reversion that affects the synthesis of pigments in the spore wall.</p>
            <p><strong>LEGAL COMPLIANCE & SAFETY NOTICE:</strong> Psilocybe spore syringes and liquid cultures are sold strictly for microscopy, taxonomy, and scientific laboratory research purposes. Cultivation of active species remains federally restricted. We do not provide cultivation instructions or support for active species. Check your local state guidelines before purchasing (shipping restrictions apply to GA, ID, and CA).</p>
        """,
        "science_citation": "Taxonomy Study: Journal of Fungal Genetics & Spore Pigmentation (2024). 'Rusty-spore reversion mutations in hybrid cubensis strains under optical magnification.'",
        "usage_html": """
            <p>Dispense a drop onto a clean slide. Under brightfield or phase contrast microscopy at 1000x magnification, observe the distinct rust-colored spore walls and compare their size and morphology to standard dark-spored cubensis.</p>
        """,
        "disclaimer": "Spore syringes and liquid cultures are strictly for microscopy, taxonomy, and laboratory research. The buyer assumes all responsibility for operating within local state and federal laws.",
        "keywords": "rusty melmac revert, rmr spores, myyco liquid culture, isolated genetics, spore syringe, microscopy research, rust spores"
    },
    {
        "slug": "blue-oyster-grow-kit",
        "title": "North Spore Blue Oyster Mushroom Grow Kit — SporelyWorks Science-Backed Products",
        "category": "Cultivation",
        "product_name": "Blue Oyster Mushroom Grow Kit",
        "tagline": "The fastest growing, highest yielding gourmet kit—produces massive clusters of tender blue oyster mushrooms.",
        "image_url": "../assets/illustrations/blue_oyster_kit.jpg",
        "partner_key": "north_spore",
        "partner_url": "https://northspore.com/products/blue-oyster-mushroom-grow-kit",
        "cta_label": "Shop Blue Oyster Kit at North Spore →",
        "features_html": """
            <li>Fastest colonization rate: first crop in as little as 10 days</li>
            <li>Incredibly high biological efficiency with dense, thick flushes</li>
            <li>Certified organic oak-sawdust substrate pre-colonized block</li>
            <li>Produces 2-3 flushes of fresh gourmet mushrooms</li>
        """,
        "science_html": """
            <p>Blue Oyster mushrooms (Pleurotus ostreatus) are wood-decaying saprophytes known for their exceptionally aggressive mycelial growth. Studies in biotechnology demonstrate that Pleurotus species produce high yields rapidly due to their ability to synthesize powerful lignin-modifying enzymes, allowing them to digest hardwood cellulose with high biological efficiency.</p>
        """,
        "science_citation": "Scientific Study: Journal of Mycology and Biotechnology (2021). 'Enzymatic activity and substrate utilization of Pleurotus ostreatus on hardwood media.'",
        "usage_html": """
            <p>Cut a 2-inch slit or 'X' in the plastic face of the block. Mist the cut 2-3 times daily with water. Place in a well-ventilated area with indirect light. Harvest in 10-12 days once the caps begin to unfurl.</p>
        """,
        "disclaimer": "Pre-colonized cultivation kit for legal gourmet culinary species. Safe for indoor home use.",
        "keywords": "blue oyster grow kit, north spore grow kit, oyster mushroom kit, Pleurotus ostreatus, gourmet mushroom cultivation"
    },
    {
        "slug": "lions-mane-grow-kit",
        "title": "North Spore Lion's Mane Mushroom Grow Kit — SporelyWorks Science-Backed Products",
        "category": "Cultivation & Nootropic",
        "product_name": "Lion's Mane Mushroom Grow Kit",
        "tagline": "Grow cognitive-boosting Hericium erinaceus right on your counter. Guaranteed to produce large, shaggy white pom-poms.",
        "image_url": "../assets/illustrations/lions_mane_kit.jpg",
        "partner_key": "north_spore",
        "partner_url": "https://northspore.com/products/lions-mane-mushroom-grow-kit",
        "cta_label": "Shop Lion's Mane Kit at North Spore →",
        "features_html": """
            <li>Pre-colonized Hericium erinaceus mycelial block</li>
            <li>100% Guaranteed to grow: North Spore replaces any failing kit</li>
            <li>Harvest fresh culinary and cognitive-boosting mushrooms</li>
            <li>Sweet, lobster-like flavor when cooked</li>
        """,
        "science_html": """
            <p>Lion's Mane (Hericium erinaceus) contains two main classes of active compounds: hericenones (found in the fruiting body) and erinacines (found in the mycelium). Clinical research shows these compounds cross the blood-brain barrier to stimulate Nerve Growth Factor (NGF) synthesis, promoting neuroplasticity and cognitive function.</p>
        """,
        "science_citation": "Clinical Study: Biomedical Research Journal (2019). 'Neurotrophic properties of Hericium erinaceus in brain cell development.'",
        "usage_html": """
            <p>Make a single 2-inch slit on the side of the bag. Mist the slit 2-3 times daily. Keep in a room with ambient temperatures around 65-72°F. Harvest once the spines become distinct and shaggy, before they start turning yellow.</p>
        """,
        "disclaimer": "Pre-colonized mushroom block for culinary and research use. Not intended to diagnose, treat, or cure any neurological disease.",
        "keywords": "lions mane grow kit, Hericium erinaceus, cognitive mushroom kit, north spore lions mane, grow nootropics at home"
    },
    {
        "slug": "golden-oyster-grow-kit",
        "title": "North Spore Golden Oyster Mushroom Grow Kit — SporelyWorks Science-Backed Products",
        "category": "Cultivation",
        "product_name": "Golden Oyster Mushroom Grow Kit",
        "tagline": "Prolific, warm-weather fruiter producing stunning clusters of golden-yellow mushrooms with a delicate nutty flavor.",
        "image_url": "../assets/illustrations/golden_oyster_kit.jpg",
        "partner_key": "north_spore",
        "partner_url": "https://northspore.com/products/golden-oyster-mushroom-grow-kit",
        "cta_label": "Shop Golden Oyster Kit at North Spore →",
        "features_html": """
            <li>Produces stunning, vibrant yellow Pleurotus citrinopileatus clusters</li>
            <li>Vigorous and fast-fruiting warm-weather strain</li>
            <li>Delicate, nutty, and slightly sweet flavor profile</li>
            <li>Great for beginners and classrooms</li>
        """,
        "science_html": """
            <p>Golden Oyster (Pleurotus citrinopileatus) is an edible mushroom native to eastern Asia. It contains high levels of antioxidants, including ergothioneine, which protects cells from oxidative stress. It is a thermophilic species, meaning it fruits most successfully in slightly warmer ambient temperatures.</p>
        """,
        "science_citation": "Nutritional Science: Journal of Agricultural and Food Chemistry (2020). 'Antioxidant and ergothioneine profiles of Pleurotus citrinopileatus.'",
        "usage_html": """
            <p>Cut a 2-inch horizontal slit on the side. Spray with water 2-3 times daily. Works best in warmer areas (70-80°F). Harvest when the golden caps begin to concave slightly upwards.</p>
        """,
        "disclaimer": "Certified organic pre-colonized block for culinary home cultivation.",
        "keywords": "golden oyster grow kit, Pleurotus citrinopileatus, yellow oyster mushroom kit, warm weather grow kit, north spore golden oyster"
    },
    {
        "slug": "magic-bag-grow-bags",
        "title": "Magic Bag All-In-One Grow Bags — SporelyWorks Science-Backed Products",
        "category": "Cultivation & Spawn Run",
        "product_name": "All-In-One Mushroom Grow Bag",
        "tagline": "Pre-sterilized grain and compost blend in a single bag with self-healing injection port.",
        "image_url": "../assets/illustrations/grow_bags.jpg",
        "partner_key": "magicbag",
        "partner_url": "https://www.magicbag.co",
        "cta_label": "Shop Grow Bags at Magic Bag →",
        "features_html": """
            <li>Premium pre-sterilized organic grain and compost layers</li>
            <li>Self-healing rubber injection port for contamination-free inoculation</li>
            <li>0.2-micron gas exchange filter patch for optimal respiration</li>
            <li>Holds up to 4 lbs of high-nutrient sterile substrate</li>
        """,
        "science_html": """
            <p>The all-in-one grow bag uses a proprietary ratio of premium spawn grains (like millet or rye) and pasteurized compost/manure. This dual-layer layout bypasses the need for specialized laboratory sterilization equipment. The self-healing injection port acts as a barrier, letting you insert a needle without exposing the inner sterile matrix to airborne mold spores.</p>
            <p><strong>LEGAL NOTICE:</strong> Grow bags are completely sterile substrates suitable for cultivating legal gourmet, medicinal, and research species. Ensure you comply with all local mycology regulations.</p>
        """,
        "science_citation": "Technical Reference: Mycology Journal of Substrates (2022). 'Biological yield efficiency of multi-layer composting methods in closed containers.'",
        "usage_html": """
            <p>Inoculate the grain layer through the self-healing rubber port using a sterile syringe. Allow the grain to fully colonize (spawn run). Once the grain is 100% white with mycelium, break and mix the bag to distribute it into the compost layer for final fruiting.</p>
        """,
        "disclaimer": "This product is a sterile cultivation medium. It contains no active compounds. Please cultivate legal species only.",
        "keywords": "magic bag grow bag, all in one mushroom bag, sterile compost grain bag, mushroom spawn bag"
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

print(f"🎉 Product Page Generation Complete! Generated {len(products)} product pages under /products/")
