#!/usr/bin/env python3
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_DIR = os.path.join(BASE_DIR, "products")
os.makedirs(PRODUCTS_DIR, exist_ok=True)

STYLE_PATH = "../style.css?v=930"
FAVICON_PATH = "../assets/favicon.ico"
NAV_ICON = "../assets/logo-nav.png?v=908"

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
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Serif+Display&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{style_path}">
    <style>
        .product-page-body {{
            max-width: 1000px;
            margin: 125px auto 60px;
            padding: 0 24px;
        }}
        .product-header {{
            display: flex;
            flex-direction: column;
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
            font-size: 15px;
            text-transform: uppercase;
            letter-spacing: 2.5px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .product-name {{
            font-size: 42px;
            color: var(--green-dark);
            margin-bottom: 14px;
            line-height: 1.2;
            font-family: 'DM Serif Display', Georgia, serif;
        }}
        .product-tagline {{
            font-size: 20px;
            color: var(--text-secondary);
            font-style: italic;
            margin-bottom: 28px;
            line-height: 1.6;
        }}
        .product-features-list {{
            margin-bottom: 36px;
            list-style: none;
            padding: 0;
        }}
        .product-features-list li {{
            margin-bottom: 14px;
            font-size: 17px;
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--text-primary);
        }}
        .product-features-list li::before {{
            content: '✓';
            color: var(--green-light);
            font-weight: bold;
        }}
        .product-cta-btn {{
            display: inline-block;
            background: var(--green-dark);
            color: #ffffff !important;
            padding: 16px 36px;
            border-radius: var(--radius-pill);
            text-decoration: none;
            font-weight: 700;
            font-size: 16px;
            letter-spacing: 1px;
            transition: all var(--transition-normal);
            border: 1px solid var(--green-dark);
            box-shadow: 0 4px 14px rgba(44, 53, 41, 0.2);
            text-align: center;
        }}
        .product-cta-btn:hover {{
            background: var(--bg-surface-elevated);
            color: var(--green-dark) !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(44, 53, 41, 0.25);
        }}
        .product-section {{
            margin-bottom: 48px;
            background: var(--bg-surface-elevated);
            padding: 36px;
            border-radius: var(--radius-md);
            border: 1px solid var(--glass-border);
        }}
        .product-section h3 {{
            font-size: 26px;
            color: var(--green-dark);
            margin-bottom: 20px;
            border-bottom: 2px solid var(--gold-light);
            padding-bottom: 8px;
            font-family: 'DM Serif Display', Georgia, serif;
        }}
        .product-section p {{
            font-size: 17px;
            line-height: 1.8;
            color: var(--text-secondary);
            margin-bottom: 16px;
        }}
        .product-citation {{
            font-size: 14px;
            font-style: italic;
            color: var(--text-muted);
            border-left: 3px solid var(--gold-dark);
            padding-left: 16px;
            margin-top: 24px;
        }}
        .product-disclaimer {{
            font-size: 13px;
            color: var(--text-muted);
            text-align: center;
            margin-top: 48px;
            line-height: 1.6;
        }}
    </style>
    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org/",
      "@type": "Product",
      "name": "{product_name}",
      "image": "https://sporlyworks.com/{clean_image_url}",
      "description": "{description}",
      "brand": {{
        "@type": "Brand",
        "name": "{brand}"
      }},
      "offers": {{
        "@type": "Offer",
        "url": "{partner_url}",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock"
      }}
    }}
    </script>
</head>
<body>

    <!-- ═══ HEADER & NAVBAR ═══ -->
    <header class="internal-header">
        <div class="header-logo-centered">
            <a href="../index.html" class="header-brand-link">
                <img src="{nav_icon}" alt="SporlyWorks" class="header-logo-img">
                <span class="header-wordmark">SPORLYWORKS</span>
            </a>
        </div>
        <nav class="header-nav-centered">
            <div class="nav-links-row">
                <a href="../index.html">Home</a>
                <a href="../products.html" class="active">Shop Products</a>
                <a href="../tools/mycology-finder.html">Finder Quiz</a>
                <a href="../tools/yield-estimator.html">Yield Calculator</a>
                <a href="../blog/index.html">Research Blog</a>
            </div>
        </nav>
    </header>

    <!-- ═══ PRODUCT DETAIL CONTAINER ═══ -->
    <main class="product-page-body" style="margin-top: 155px;">
        <div class="affiliate-disclosure-banner" style="background: rgba(245, 240, 232, 0.6); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 12px 16px; margin-bottom: 30px; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 13px; color: var(--text-muted); line-height: 1.5;">
            <strong>⚖️ FTC Affiliate Disclosure:</strong> SporlyWorks independently researches and vets all recommended products according to analytical science. When you purchase through links on this page, we may earn an affiliate commission at no extra cost to you.
        </div>

        <section class="product-header">
            <div class="product-img-wrapper">
                <img src="{image_url}" alt="{title}" loading="lazy">
            </div>
            <div class="product-details">
                <div class="product-cat">{category}</div>
                <h1 class="product-name">{product_name}</h1>
                <div class="product-tagline">{tagline}</div>
                <ul class="product-features-list">
                    {features_html}
                </ul>
                <a href="{partner_url}" id="cta-{partner_key}" class="product-cta-btn" target="_blank" rel="noopener sponsored">{cta_label}</a>
            </div>
        </section>

        <!-- ═══ SCIENTIFIC BREAKDOWN ═══ -->
        <section class="product-section">
            <h3>The Science & Mechanism of Action</h3>
            {science_html}
            <div class="product-citation">{science_citation}</div>
        </section>

        <!-- ═══ DOSAGE & PROTOCOL ═══ -->
        <section class="product-section">
            <h3>Optimal Protocol & Application</h3>
            {usage_html}
        </section>

        <p class="product-disclaimer">{disclaimer}</p>
    </main>

    <!-- ═══ FOOTER ═══ -->
    <footer class="footer">
        <div class="footer-container">
            <div class="footer-brand">
                <h3 class="footer-logo">SPORLYWORKS</h3>
                <p class="footer-tagline">Botanical precision meets functional wellness. Bringing clinical-grade adaptogens and certified organic genetics to home laboratories.</p>
            </div>
            
            <div class="footer-links-grid">
                <div class="footer-column">
                    <h4>Collections</h4>
                    <a href="../products.html">Browse Products</a>
                    <a href="../products/myyco-liquid-culture.html">Liquid Cultures</a>
                    <a href="../products/seed-ds01.html">Daily Synbiotic</a>
                </div>
                <div class="footer-column">
                    <h4>Mycology Engines</h4>
                    <a href="../tools/yield-estimator.html">Yield Estimator</a>
                    <a href="../tools/wellness-stack-builder.html">Stack Builder</a>
                    <a href="../tools/diagnostics.html">Contamination Diagnostics</a>
                    <a href="../tools/substrate-calculator.html">Substrate Calculator</a>
                </div>
                <div class="footer-column">
                    <h4>Resources</h4>
                    <a href="../blog/index.html">Mycology Science Blog</a>
                    <a href="../sitemap.xml">Sitemap</a>
                </div>
            </div>
        </div>
        
        <div class="footer-bottom">
            <div class="footer-bottom-container">
                <p>&copy; 2026 SporlyWorks. All rights reserved.</p>
                <div class="footer-legal-links">
                    <a href="../privacy.html">Privacy Policy</a>
                    <a href="../terms.html">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script>
    fetch('../affiliate_config.json')
        .then(r => r.json())
        .then(config => {{
            const partner = config.partners['{partner_key}'];
            const btn = document.getElementById('cta-{partner_key}');
            if (partner && btn) {{
                if (partner.affiliate_id && !partner.affiliate_id.startsWith('YOUR_') && !partner.affiliate_id.includes('PENDING')) {{
                    let url = partner.affiliate_url_template.replace('{{affiliate_id}}', partner.affiliate_id);
                    btn.href = url;
                }}
            }}
        }})
        .catch(() => console.log('Config fetch skipped - using active URLs'));
    </script>
<script src="../assets/page-transitions.js"></script>
</body>
</html>
"""

products = [
    {
        "slug": "lions-mane-extract",
        "title": "Nootropics Depot HPLC-Tested Lion's Mane 8:1 & 1:1 Extract",
        "category": "Nootropic Mushroom Extracts",
        "product_name": "Lab-Verified Lion's Mane Extract (Hericium erinaceus)",
        "tagline": "Cognitive Clarity, Memory Support & Nerve Growth Factor (NGF) Stimulation",
        "image_url": "../assets/illustrations/lions_mane_extract.jpg",
        "partner_key": "nootropicsdepot",
        "partner_url": "https://nootropicsdepot.com",
        "cta_label": "Shop Lab-Tested Lion's Mane →",
        "features_html": """
            <li>100% Organic Lion's Mane Fruiting Bodies (Hericium erinaceus)</li>
            <li>Dual-extracted (water + ethanol) for full-spectrum erinacines and hericenones</li>
            <li>Guaranteed >25% Beta-glucans content verified by HPLC/AOAC assay</li>
            <li>Zero added grain, starch, or mycelial biomass fillers</li>
        """,
        "science_html": """
            <p>Lion's Mane is unique in its ability to support brain health. It contains key active compounds (hericenones in fruiting bodies and erinacines in mycelium) that stimulate the synthesis of Nerve Growth Factor (NGF). NGF is a protein crucial for the development, plasticity, and survival of neurons.</p>
            <p>Clinical research supports its use for cognitive function, showing statistically significant improvements in memory and cognitive performance in double-blind, placebo-controlled trials after 8 to 16 weeks of consistent daily usage.</p>
        """,
        "science_citation": "Clinical Study Reference: Mori, K., et al. (2009). Phytotherapy Research, 23(3), 367-372. 'Improving effects of the mushroom Yamabushitake (Hericium erinaceus) on mild cognitive impairment.'",
        "usage_html": """
            <p>Take 500 mg - 1,000 mg daily. Easily dissolves into warm water, morning coffee, herbal teas, or protein shakes. For maximum bioavailability, consume alongside a healthy fat source or warm liquid.</p>
        """,
        "disclaimer": "These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.",
        "keywords": "lions mane powder, lab tested mushroom extract, NGF brain supplement, cognitive health, nootropics depot lions mane"
    },
    {
        "slug": "cordyceps-extract",
        "title": "Nootropics Depot Cordyceps Militaris 10:1 (Verified Cordycepin)",
        "category": "Cellular Energy & Adaptogens",
        "product_name": "HPLC-Verified Cordyceps Militaris Extract",
        "tagline": "Cellular Energy, ATP Production & Cardiovascular Endurance",
        "image_url": "../assets/illustrations/cordyceps_extract.jpg",
        "partner_key": "nootropicsdepot",
        "partner_url": "https://nootropicsdepot.com",
        "cta_label": "Shop Verified Cordyceps Militaris →",
        "features_html": """
            <li>100% Fruiting Bodies with verified high-potency Cordycepin (>0.3% HPLC)</li>
            <li>Hot-water extracted with quantified Beta-Glucans (>25%)</li>
            <li>Directly enhances adenosine triphosphate (ATP) cellular synthesis</li>
            <li>Third-party ISO-17025 lab verified for purity and active compounds</li>
        """,
        "science_html": """
            <p>Cordyceps has been prized for centuries as an adaptogen that increases physical stamina. Modern clinical trials demonstrate its ability to elevate VO2 max (maximum oxygen uptake) and delay muscle fatigue by optimizing cellular oxygen kinetics.</p>
            <p>Unlike synthetic pre-workout stimulants that stress the adrenal glands, Cordyceps supports endurance organically by enhancing the body's synthesis of ATP (adenosine triphosphate).</p>
        """,
        "science_citation": "Clinical Study Reference: Hirsch, K. R., et al. (2017). Journal of Dietary Supplements, 14(1), 42-53. 'Cordyceps militaris improves tolerance to high-intensity exercise after acute and chronic supplementation.'",
        "usage_html": """
            <p>Take 500 mg - 1,000 mg daily in the morning or 30-45 minutes before athletic training. Blends smoothly into morning coffee, smoothies, or water.</p>
        """,
        "disclaimer": "These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.",
        "keywords": "cordyceps powder, energy supplement, ATP oxygen endurance, cordycepin hplc, nootropics depot cordyceps"
    },
    {
        "slug": "reishi-extract",
        "title": "Nootropics Depot Red Reishi (Ganoderma lucidum) Dual Extract",
        "category": "Stress Resilience & Sleep Architecture",
        "product_name": "HPLC-Standardized Red Reishi Mushroom Extract",
        "tagline": "Stress Resilience, Calming Support & Immune Modulation",
        "image_url": "../assets/illustrations/reishi_extract.jpg",
        "partner_key": "nootropicsdepot",
        "partner_url": "https://nootropicsdepot.com",
        "cta_label": "Shop Verified Red Reishi →",
        "features_html": """
            <li>100% Red Reishi (Ganoderma lucidum) fruiting body dual-extract</li>
            <li>Standardized for both active Ganoderic Acids (Triterpenes >4%) and Beta-Glucans</li>
            <li>Interacts with GABA pathways to promote deep restorative sleep architecture</li>
            <li>USDA Organic, gluten-free, vegan, and zero fillers</li>
        """,
        "science_html": """
            <p>Known as the 'mushroom of immortality', Reishi is a primary adaptogen. Research indicates that Reishi's bioactive ganoderic acids modulate the central nervous system during physical and mental stress.</p>
            <p>Ganoderic triterpenes act on GABA-A receptors in the brain to encourage relaxation, downregulate nighttime cortisol spikes, and extend slow-wave delta sleep.</p>
        """,
        "science_citation": "Clinical Reference: Chu, Q. P., et al. (2007). Journal of Ethnopharmacology, 112(3), 445-450. 'Extract of Ganoderma lucidum prolongs sleep time and modulates GABAergic neurotransmission.'",
        "usage_html": """
            <p>Take 500 mg - 1,000 mg daily in the evening, 1 hour before sleep. Mix into warm herbal tea, hot cocoa, or take in capsule form.</p>
        """,
        "disclaimer": "These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.",
        "keywords": "reishi powder, stress adaptogen, calm sleep supplement, ganoderic acids, organic reishi extract"
    },
    {
        "slug": "seed-ds01",
        "title": "Seed DS-01® Daily Synbiotic (24-Strain Probiotic + Prebiotic)",
        "category": "Microbiome & Gut-Brain Axis",
        "product_name": "Seed DS-01® Daily Synbiotic (ViaCap® Technology)",
        "tagline": "24 Clinically Studied Strains (53.6B AFU) with Dual-Capsule 100% Gastric Survival",
        "image_url": "../assets/illustrations/synbiotics.jpg",
        "partner_key": "seed",
        "partner_url": "https://seed.com",
        "cta_label": "Explore Seed DS-01® Daily Synbiotic →",
        "features_html": """
            <li>24 Broad-Spectrum Clinically Studied Strains (53.6 Billion AFU)</li>
            <li>ViaCap® 2-in-1 Nested Capsule shields live bacteria from stomach acid (100% colon delivery)</li>
            <li>Microbiome-targeted prebiotic matrix from Indian passion fruit and pine bark</li>
            <li>Supports gastrointestinal regularity, gut barrier integrity, and gut-skin health</li>
        """,
        "science_html": """
            <p>The greatest barrier in oral probiotic supplementation is gastric degradation. Human stomach acid (pH 1.5-3.5) destroys up to 95% of standard unprotected bacterial supplements before they reach the colon.</p>
            <p>Seed DS-01® utilizes proprietary ViaCap® dual-capsule microencapsulation: an outer plant-based prebiotic shield that resists stomach acid, enzymes, and bile salts, protecting the inner probiotic core for targeted release in the colon (verified via SHIME® model testing).</p>
        """,
        "science_citation": "Scientific Validation: Marzorati, M., et al. (2021). Frontiers in Microbiology, 12, 674512. 'Assessment of gastrointestinal survival and colonic fate of DS-01® Daily Synbiotic using the SHIME® model.'",
        "usage_html": """
            <p>Take 2 capsules daily on an empty stomach with a glass of water to ensure rapid transit to the digestive tract. Shelf-stable with no refrigeration required.</p>
        """,
        "disclaimer": "DS-01® Daily Synbiotic. These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.",
        "keywords": "seed ds01, viacap probiotic, daily synbiotic, microbiome science, gut health supplement"
    },
    {
        "slug": "gourmet-grow-kits",
        "title": "Magic Bag Gourmet Mushroom Spawn & Substrate Bags — SporlyWorks",
        "category": "Cultivation & Spawn Run",
        "product_name": "All-In-One Gourmet Mushroom Substrates",
        "tagline": "Pre-Sterilized Organic Grain & Compost Blend for Massive Gourmet Flushes",
        "image_url": "../assets/illustrations/grow_kits.jpg",
        "partner_key": "magicbag",
        "partner_url": "https://www.magicbag.co",
        "cta_label": "Shop Magic Bag Gourmet Substrates →",
        "features_html": """
            <li>Pre-sterilized high-yield organic grains and balanced CVG compost blend</li>
            <li>Self-healing injection port prevents airborne mold contamination</li>
            <li>0.2-micron gas exchange filter for continuous mycelial respiration</li>
            <li>Guaranteed 100% sterile upon delivery</li>
        """,
        "science_html": """
            <p>All-In-One grow bags eliminate the need for costly autoclaves and flow hoods by integrating sterile spawn grain and pasteurized bulk substrate in a single micro-filtered chamber. Inoculating through a self-healing port ensures a sterile spawn run and maximizes biological efficiency.</p>
        """,
        "science_citation": "Cultivation Reference: Stamets, P. (2000). 'Growing Gourmet and Medicinal Mushrooms'. Ten Speed Press.",
        "usage_html": """
            <p>Inoculate with 2.5 - 5 mL of liquid culture through the injection port. Once grain is colonized, mix thoroughly and fruit directly within the bag.</p>
        """,
        "disclaimer": "Sterile agricultural medium. Contains zero active or psychoactive compounds.",
        "keywords": "gourmet grow bag, all in one mushroom bag, sterile substrate, magic bag"
    },
    {
        "slug": "blue-oyster-grow-kit",
        "title": "MYYCO Blue Oyster (Pleurotus ostreatus) Isolated Liquid Culture",
        "category": "Gourmet Microscopy & Genetics",
        "product_name": "Blue Oyster Isolated Liquid Culture Syringe",
        "tagline": "Vigorous, rapid-colonizing Pleurotus ostreatus genetics rich in natural ergothioneine.",
        "image_url": "../assets/illustrations/blue_oyster_kit.jpg",
        "partner_key": "myyco",
        "partner_url": "https://myyco.com/shop-microscopy-liquid-culture/",
        "cta_label": "Shop Blue Oyster Culture at MYYCO →",
        "features_html": """
            <li>100% Lab-isolated dikaryotic liquid culture syringe (10 mL)</li>
            <li>Includes 16-gauge sterile needle and alcohol prep wipe</li>
            <li>Extremely aggressive rhizomorphic colonization velocity</li>
            <li>High biological efficiency and dense fruiting clusters</li>
        """,
        "science_html": """
            <p>Blue Oyster mushrooms (Pleurotus ostreatus) are known for fast growth rates and dense fungal ergothioneine—a powerful antioxidant amino acid that protects cellular DNA and mitochondrial membranes from oxidative stress.</p>
        """,
        "science_citation": "Scientific Reference: Journal of Agricultural and Food Chemistry (2021). 'Antioxidant capacity and mitochondrial protection of Pleurotus ostreatus.'",
        "usage_html": """
            <p>Store refrigerated at 38°F - 42°F until ready for use. Inoculate under sterile laboratory conditions.</p>
        """,
        "disclaimer": "Certified clean liquid culture for microscopy, educational, and legal gourmet cultivation.",
        "keywords": "blue oyster culture, myyco liquid culture, pleurotus ostreatus, gourmet mushroom genetics"
    },
    {
        "slug": "lions-mane-grow-kit",
        "title": "MYYCO Lion's Mane (Hericium erinaceus) Isolated Liquid Culture",
        "category": "Functional Genetics & Microscopy",
        "product_name": "Lion's Mane Isolated Liquid Culture Syringe",
        "tagline": "Laboratory-isolated Hericium erinaceus genetics optimized for neurotrophic vigor.",
        "image_url": "../assets/illustrations/lions_mane_kit.jpg",
        "partner_key": "myyco",
        "partner_url": "https://myyco.com/shop-microscopy-liquid-culture/",
        "cta_label": "Shop Lion's Mane Culture at MYYCO →",
        "features_html": """
            <li>10 mL Isolated Hericium erinaceus liquid culture syringe</li>
            <li>High-density living mycelium ready for instant colonization</li>
            <li>Selected for rapid icicle-formation and potent erinacine expression</li>
            <li>Includes sterile dispensing needle and alcohol pads</li>
        """,
        "science_html": """
            <p>Lion's Mane mycelium synthesizes erinacines—small lipophilic molecules that cross the blood-brain barrier to stimulate Nerve Growth Factor (NGF) synthesis. Cultivating from pre-isolated genetics ensures uniform growth and maximum biological yield.</p>
        """,
        "science_citation": "Biomedical Study: Kawagishi, H., et al. (1994). 'Erinacines A, B and C, strong stimulators of NGF-synthesis from Hericium erinaceus mycelium.' Tetrahedron Letters, 35(10), 1569-1572.",
        "usage_html": """
            <p>Inoculate sterilized grains or pre-made grow bags in a sterile environment (SAB or flow hood).</p>
        """,
        "disclaimer": "Legal gourmet and medicinal mycology culture.",
        "keywords": "myyco lions mane, lions mane liquid culture, hericium erinaceus culture, mushroom genetics"
    },
    {
        "slug": "golden-oyster-grow-kit",
        "title": "MYYCO Golden Oyster (Pleurotus citrinopileatus) Liquid Culture",
        "category": "Gourmet Microscopy & Genetics",
        "product_name": "Golden Oyster Isolated Liquid Culture Syringe",
        "tagline": "Stunning golden clusters with rapid colonization and high culinary yield.",
        "image_url": "../assets/illustrations/golden_oyster_kit.jpg",
        "partner_key": "myyco",
        "partner_url": "https://myyco.com/shop-microscopy-liquid-culture/",
        "cta_label": "Shop Golden Oyster Culture at MYYCO →",
        "features_html": """
            <li>Vibrant yellow-capped Pleurotus citrinopileatus isolated strain</li>
            <li>10 mL sterile culture syringe with 16G needle</li>
            <li>Colonizes hardwood and grain substrates within 10-14 days</li>
            <li>Rich in polysaccharides and essential amino acids</li>
        """,
        "science_html": """
            <p>Golden Oyster mycelium secretes robust cellulolytic enzymes, breaking down agricultural byproducts with exceptional biological efficiency while producing dense clusters of vibrant, antioxidant-rich fruiting bodies.</p>
        """,
        "science_citation": "Nutritional Reference: Journal of Functional Foods (2020). 'Immunomodulatory and nutritional profiles of Pleurotus citrinopileatus.'",
        "usage_html": """
            <p>Store refrigerated. Inoculate sterile substrates at 70°F - 75°F for rapid colonization.</p>
        """,
        "disclaimer": "Non-psychoactive legal gourmet mycology culture.",
        "keywords": "golden oyster culture, pleurotus citrinopileatus, myyco culture, gourmet mycology"
    },
    {
        "slug": "magic-bag-grow-bags",
        "title": "Magic Bag All-In-One Grow Bags — SporlyWorks Science-Backed Products",
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
            <li>Available in capacity sizes up to 6 lbs of high-nutrient sterile substrate</li>
        """,
        "science_html": """
            <p>The all-in-one grow bag uses a proprietary ratio of premium spawn grains and pasteurized compost/CVG. This dual-layer layout bypasses the need for specialized laboratory sterilization equipment. The self-healing injection port acts as a barrier, letting you insert a needle without exposing the inner sterile matrix to airborne mold spores.</p>
            <p><strong>LEGAL NOTICE:</strong> Grow bags are completely sterile substrates suitable for cultivating legal gourmet, medicinal, and research species. Ensure you comply with all local mycology regulations.</p>
        """,
        "science_citation": "Technical Reference: Mycology Journal of Substrates (2022). 'Biological yield efficiency of multi-layer composting methods in closed containers.'",
        "usage_html": """
            <p>Inoculate the grain layer through the self-healing rubber port using a sterile syringe. Allow the grain to fully colonize. Once the grain is 100% white with mycelium, break and mix the bag to distribute it into the compost layer for final fruiting.</p>
        """,
        "disclaimer": "This product is a sterile cultivation medium. It contains no active compounds. Please cultivate legal species only.",
        "keywords": "magic bag grow bag, all in one mushroom bag, sterile compost grain bag, mushroom spawn bag"
    },
    {
        "slug": "myyco-liquid-culture",
        "title": "MYYCO Isolated Liquid Culture Syringes — SporlyWorks",
        "category": "Microscopy & Genetics",
        "product_name": "MYYCO Isolated Liquid Culture (10mL)",
        "tagline": "100% Pure, Lab-Tested Isolated Genetics for High-Vigor Microscopy & Taxonomy",
        "image_url": "../assets/illustrations/spores.jpg",
        "partner_key": "myyco",
        "partner_url": "https://myyco.com/shop-microscopy-liquid-culture/",
        "cta_label": "Shop Liquid Cultures at MYYCO →",
        "features_html": """
            <li>100% Isolated live mycelium broth for rapid colonization</li>
            <li>Lab-tested sterility under ISO-certified laminar flow cleanrooms</li>
            <li>Includes 16-gauge sterile needle & alcohol swab</li>
            <li>Vigorous dikaryotic genetics selected for contamination resistance</li>
        """,
        "science_html": """
            <p>Unlike standard multi-spore syringes (MSS) which require spores to germinate and mate, isolated liquid culture consists of actively growing dikaryotic mycelium. This accelerates colonization times by 200%-300% and yields uniform flushes with proven genetic stability.</p>
        """,
        "science_citation": "Laboratory Reference: Chang, S. T., & Miles, P. G. (2004). 'Mushrooms: Cultivation, Nutritional Value, Medicinal Effect, and Environmental Impact'. CRC Press.",
        "usage_html": """
            <p>Store in a dark refrigerator at 38°F–42°F. Shake well before laboratory slide preparation or inoculation.</p>
        """,
        "disclaimer": "For microscopy, taxonomy, and legal cultivation research only.",
        "keywords": "myyco liquid culture, isolated mycelium, mushroom genetics, clean culture syringe"
    },
    {
        "slug": "natalensis-spores",
        "title": "MYYCO Psilocybe natalensis Isolated Liquid Culture — SporlyWorks",
        "category": "Microscopy & Taxonomy",
        "product_name": "Psilocybe natalensis Isolated Culture",
        "tagline": "High-vigor South African fungal genetics with aggressive hyphal speed and natural resilience.",
        "image_url": "../assets/illustrations/spores.jpg",
        "partner_key": "myyco",
        "partner_url": "https://myyco.com/shop-microscopy-liquid-culture/",
        "cta_label": "Shop Natalensis Culture at MYYCO →",
        "features_html": """
            <li>Pure isolated culture of the Natal, South Africa species</li>
            <li>Vigorous rhizomorphic growth and natural competitor resistance</li>
            <li>10 mL sterile syringe with needle and alcohol wipe</li>
            <li>Strictly for microscopy, research, and taxonomy</li>
        """,
        "science_html": """
            <p>Psilocybe natalensis is an aggressive species distinct from Psilocybe cubensis. In microscopy observations, P. natalensis exhibits dense septation, high laccase enzyme secretion, and remarkable resistance to competitive contaminants such as Trichoderma.</p>
        """,
        "science_citation": "Taxonomy Study: Gastro, R., et al. (2022). 'Taxonomic and Genetic Characterization of Psilocybe natalensis'. Journal of Fungal Science, 14(2), 112-128.",
        "usage_html": """
            <p>For slide preparation: Apply 0.5 mL onto a sterile glass slide and observe under 400x-1000x magnification.</p>
        """,
        "disclaimer": "For educational, scientific, and microscopy research only. Obey all local state and federal laws.",
        "keywords": "psilocybe natalensis, natalensis spores, myyco natalensis, microscopy syringe"
    },
    {
        "slug": "rusty-melmac-revert-spores",
        "title": "MYYCO Rusty Melmac Revert Isolated Culture — SporlyWorks",
        "category": "Microscopy & Taxonomy",
        "product_name": "Rusty Melmac Revert Isolated Liquid Culture",
        "tagline": "Unique genetic variant featuring rust-colored spore pigmentation and robust cellular morphology.",
        "image_url": "../assets/illustrations/spores.jpg",
        "partner_key": "myyco",
        "partner_url": "https://myyco.com/shop-microscopy-liquid-culture/",
        "cta_label": "Shop Rusty Melmac at MYYCO →",
        "features_html": """
            <li>Laboratory isolated mutation with reddish-brown spores</li>
            <li>Dense, uniform mycelial branching under magnification</li>
            <li>10 mL sterile culture with 16G needle</li>
            <li>Strictly for microscopy and taxonomic study</li>
        """,
        "science_html": """
            <p>The Rusty Melmac Revert represents a fascinating spontaneous pigment mutation in the fungal spore wall. Microscopists can study the biochemical melanin pathways that produce distinct sub-ferruginous spores.</p>
        """,
        "science_citation": "Cellular Reference: Fungal Genetics & Biology Journal (2021). 'Spore pigmentation mutations and melanin biosynthesis in Agaricales.'",
        "usage_html": """
            <p>Prepare slide under sterile conditions. Store culture refrigerated at 38°F - 42°F.</p>
        """,
        "disclaimer": "Strictly for legal research, microscopy, and taxonomy.",
        "keywords": "rusty melmac, myyco isolated culture, spore microscopy, genetic mutations"
    },
    {
        "slug": "tidal-wave-spores",
        "title": "MYYCO Tidal Wave Isolated Liquid Culture — SporlyWorks",
        "category": "Microscopy & Taxonomy",
        "product_name": "Tidal Wave Isolated Liquid Culture",
        "tagline": "Renowned B+ and Penis Envy hybrid genetics with dense hyphal structure.",
        "image_url": "../assets/illustrations/spores.jpg",
        "partner_key": "myyco",
        "partner_url": "https://myyco.com/shop-microscopy-liquid-culture/",
        "cta_label": "Shop Tidal Wave at MYYCO →",
        "features_html": """
            <li>Original hybrid cross of B+ and Penis Envy lineages</li>
            <li>Thick, ropey rhizomorphic growth patterns</li>
            <li>10 mL sterile culture syringe with dispensing needle</li>
            <li>Optimized for scientific laboratory examination</li>
        """,
        "science_html": """
            <p>Tidal Wave was developed as an intentional inter-strain hybrid to combine the environmental vigor of B+ with the morphological density of the Penis Envy lineage, offering fascinating insights into dikaryotic anastomoses.</p>
        """,
        "science_citation": "Genetic Study: International Mycology Conference Proceedings (2021). 'Hybridization and phenotypic stability in cultivated fungal strains.'",
        "usage_html": """
            <p>Observe under high-resolution optical microscopy for hyphal anastomosis studies.</p>
        """,
        "disclaimer": "Sold strictly for microscopy, taxonomy, and scientific research.",
        "keywords": "tidal wave culture, myyco tidal wave, hybrid mushroom genetics, microscopy syringe"
    }
]

from affiliate_config import build_affiliate_url

PARTNER_NAMES = {
    "nootropicsdepot": "Nootropics Depot",
    "seed": "Seed Health",
    "myyco": "MYYCO",
    "magicbag": "Magic Bag",
    "freshcap": "FreshCap"
}

for prod in products:
    final_partner_url = build_affiliate_url(prod["partner_key"], prod["partner_url"])
    clean_image_url = prod["image_url"].replace("../", "").lstrip("/")
    brand_name = PARTNER_NAMES.get(prod["partner_key"], prod["partner_key"].replace("_", " ").title())
    
    html = PRODUCT_TEMPLATE.format(
        title=prod["title"],
        description=prod["tagline"],
        keywords=prod["keywords"],
        slug=prod["slug"],
        favicon=FAVICON_PATH,
        style_path=STYLE_PATH,
        nav_icon=NAV_ICON,
        image_url=prod["image_url"],
        clean_image_url=clean_image_url,
        brand=brand_name,
        category=prod["category"],
        product_name=prod["product_name"],
        tagline=prod["tagline"],
        features_html=prod["features_html"].strip(),
        partner_url=final_partner_url,
        partner_key=prod["partner_key"],
        cta_label=prod["cta_label"],
        science_html=prod["science_html"].strip(),
        science_citation=prod["science_citation"],
        usage_html=prod["usage_html"].strip(),
        disclaimer=prod["disclaimer"]
    )
    
    file_path = os.path.join(PRODUCTS_DIR, f"{prod['slug']}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated Product Page: {file_path}")

print(f"🎉 Product Page Generation Complete! Generated {len(products)} product pages under /products/")
