#!/usr/bin/env python3
import os
import json

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
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
            font-weight: 800;
            font-size: 18px;
        }}
        .product-cta-btn {{
            display: inline-block;
            background: linear-gradient(135deg, var(--green-light), var(--green));
            color: white;
            padding: 16px 40px;
            border-radius: var(--radius-pill);
            text-decoration: none;
            font-weight: 700;
            font-size: 17px;
            transition: all 0.3s;
            box-shadow: 0 4px 14px rgba(11, 74, 46, 0.2);
        }}
        .product-cta-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(11, 74, 46, 0.3);
        }}
        .science-section {{
            background: var(--bg-surface-elevated);
            padding: 44px;
            border-radius: var(--radius-md);
            border: 1px solid var(--glass-border);
            margin-bottom: 48px;
            box-shadow: var(--shadow-soft);
        }}
        .science-section h3 {{
            color: var(--green);
            font-size: 26px;
            margin-bottom: 18px;
            font-family: 'DM Serif Display', Georgia, serif;
        }}
        .science-section p {{
            font-size: 17.5px;
            line-height: 1.8;
            color: var(--text-primary);
            margin-bottom: 18px;
        }}
        .science-ref {{
            font-size: 13.5px;
            color: var(--text-muted);
            font-style: italic;
            border-top: 1px solid var(--glass-border);
            padding-top: 14px;
            margin-top: 18px;
        }}
        .usage-section h3 {{
            color: var(--green-dark);
            font-size: 26px;
            margin-bottom: 18px;
            font-family: 'DM Serif Display', Georgia, serif;
        }}
        .usage-section p {{
            font-size: 17.5px;
            line-height: 1.8;
            color: var(--text-primary);
            margin-bottom: 24px;
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
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{tagline}">
    <meta property="og:type" content="product">
    <meta property="og:site_name" content="SporlyWorks">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "{product_name}",
      "description": "{tagline}",
      "image": "https://sporlyworks.com/{clean_image_url}",
      "brand": {{
        "@type": "Brand",
        "name": "{brand}"
      }},
      "url": "https://sporlyworks.com/products/{slug}.html",
      "offers": {{
        "@type": "Offer",
        "url": "{partner_url}"
      }}
    }}
    </script>
</head>
<body>

    <!-- ═══ CENTERED HEADER & NAVBAR ═══ -->
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

    <!-- ═══ MAIN CONTENT ═══ -->
    <main class="product-page-body" style="margin-top: 155px;">
        
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
            <strong>FDA & FTC Affiliate Disclosure:</strong> SporlyWorks earns an affiliate commission on qualifying purchases made through partner links at no extra cost to you. {disclaimer}
        </div>
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
                const isPlaceholder = !partner.affiliate_id || 
                                      partner.affiliate_id.startsWith('YOUR_') || 
                                      partner.affiliate_id.includes('INSERT');
                
                // For partners with hardcoded IDs, URL is already rendered correctly by Python
                if (partner.affiliate_id === 'SporlyWorks' || partner.affiliate_id === 'Sporlyworks') {{
                    return; // Already set by template
                }}

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
    </script>
<script src="../assets/page-transitions.js"></script>
</body>
</html>
"""

products = [
    {
        "slug": "lions-mane-extract",
        "title": "FreshCap Organic Lion's Mane Powder",
        "category": "Supplements",
        "product_name": "Organic Lion's Mane Extract Powder",
        "tagline": "Cognitive Clarity, Memory Support & Nerve Growth Factor (NGF) Stimulation",
        "image_url": "../assets/illustrations/lions_mane_extract.jpg",
        "partner_key": "freshcap",
        "partner_url": "https://freshcap.com",
        "cta_label": "Shop Lion's Mane at FreshCap →",
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
        "keywords": "lions mane powder, organic mushroom extract, NGF brain supplement, cognitive health, freshcap lions mane"
    },
    {
        "slug": "cordyceps-extract",
        "title": "FreshCap Organic Cordyceps Powder",
        "category": "Supplements",
        "product_name": "Organic Cordyceps Militaris Extract Powder",
        "tagline": "Cellular Energy, ATP Production & Cardiovascular Endurance",
        "image_url": "../assets/illustrations/cordyceps_extract.jpg",
        "partner_key": "freshcap",
        "partner_url": "https://freshcap.com",
        "cta_label": "Shop Cordyceps at FreshCap →",
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
        "keywords": "cordyceps powder, energy supplement, ATP oxygen endurance, freshcap cordyceps, adaptogen energy"
    },
    {
        "slug": "reishi-extract",
        "title": "FreshCap Organic Reishi Powder",
        "category": "Supplements",
        "product_name": "Organic Reishi Mushroom Extract Powder",
        "tagline": "Stress Resilience, Calming Support & Immune Modulation",
        "image_url": "../assets/illustrations/reishi_extract.jpg",
        "partner_key": "freshcap",
        "partner_url": "https://freshcap.com",
        "cta_label": "Shop Reishi at FreshCap →",
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
        "keywords": "reishi powder, stress adaptogen, calm sleep supplement, freshcap reishi, organic ganoderma extract"
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
            <p>Seed's DS-01® Daily Synbiotic is validated through in vitro SHIME® (Simulator of the Human Intestinal Microbial Ecosystem) digestive modeling. The proprietary <strong>ViaCap® 2-in-1 nested capsule technology</strong> protects live bacterial strains against 100% of gastric acid and bile salts, delivering 53.6 Billion AFU directly to the colon where microbial absorption occurs.</p>
            <p>Formulated with 24 bio-fermented, human-derived probiotic strains, DS-01® is clinically demonstrated to support gastrointestinal motility, gut barrier defense, dermatological resilience, cardiovascular homeostasis, and endogenous folate synthesis. #SeedPartner</p>
        """,
        "science_citation": "Clinical & Lab Reference: Seed Health Scientific Advisory Board (2020-2026). SHIME® GI simulation models and human double-blind clinical trials for DS-01® ViaCap® delivery.",
        "usage_html": """
            <p>Take 2 capsules daily, preferably all at once on an empty stomach to limit exposure to digestive enzymes. Start with 1 capsule daily for the first 3 days to allow your gut microbiome to adjust, then increase to the full 2-capsule daily dose.</p>
        """,
        "disclaimer": "#SeedPartner Disclosure: These statements have not been evaluated by the Food and Drug Administration. Seed products are not intended to diagnose, treat, cure, or prevent any disease. Store in a cool, dry place. No refrigeration required.",
        "keywords": "seed probiotic, ds01 synbiotic, gut microbiome health, gut barrier integrity, dual capsule probiotic, seed partner"
    },
    {
        "slug": "gourmet-grow-kits",
        "title": "Real Mushrooms Organic Gourmet Cultivation & Extracts — SporelyWorks",
        "category": "Cultivation & Wellness",
        "product_name": "Gourmet Mushroom Cultivation & Extract Line",
        "tagline": "100% Organic Fruiting Body Extracts & Cultivation Science",
        "image_url": "../assets/illustrations/grow_kits.jpg",
        "partner_key": "realmushrooms",
        "partner_url": "https://www.realmushrooms.com",
        "cta_label": "Shop Real Mushrooms Collection →",
        "features_html": """
            <li>100% Organic hot-water extracted fruiting body extracts</li>
            <li>No starch, grain fillers, or mycelium on grain additives</li>
            <li>Third-party lab tested for verified beta-glucan content (>25%)</li>
            <li>Available in organic powders and vegan capsules</li>
        """,
        "science_html": """
            <p>Real Mushrooms produces 100% organic mushroom extracts strictly from natural fruiting bodies, bypassing cheap grain fillers. Scientific analysis shows that grain-grown mycelium products often contain up to 70% starch from grain substrates, whereas hot-water extracted fruiting bodies deliver concentrated bioactive beta-glucans and triterpenes.</p>
        """,
        "science_citation": "Mycology Reference: Chilton, N. (2020). 'Analytical comparison of beta-glucan vs starch content in mushroom fruiting bodies vs grain-grown mycelium.'",
        "usage_html": """
            <p>Mix 1/2 tsp (1,000mg) into coffee, tea, smoothies, or water daily. Can be taken with or without food.</p>
        """,
        "disclaimer": "100% Organic Mushroom Extract. These statements have not been evaluated by the FDA.",
        "keywords": "real mushrooms, organic mushroom extract, beta glucan supplement, lions mane powder, gourmet mushroom extract"
    },
    {
        "slug": "blue-oyster-grow-kit",
        "title": "Real Mushrooms Gourmet Blue Oyster Extract — SporelyWorks",
        "category": "Cultivation & Wellness",
        "product_name": "Blue Oyster Mushroom Extract",
        "tagline": "Concentrated 100% organic Pleurotus ostreatus extract rich in antioxidants and ergothioneine.",
        "image_url": "../assets/illustrations/blue_oyster_kit.jpg",
        "partner_key": "realmushrooms",
        "partner_url": "https://www.realmushrooms.com",
        "cta_label": "Shop Real Mushrooms →",
        "features_html": """
            <li>Concentrated organic Pleurotus ostreatus fruiting body extract</li>
            <li>High biological active yield: rich in natural ergothioneine</li>
            <li>Certified organic, non-GMO, and gluten-free</li>
            <li>Zero added grain, starch, or filler ingredients</li>
        """,
        "science_html": """
            <p>Blue Oyster mushrooms (Pleurotus ostreatus) are celebrated for their rich antioxidant profile, particularly ergothioneine—a specialized amino acid derivative that scavenges free radicals and protects cellular mitochondria from oxidative degradation.</p>
        """,
        "science_citation": "Scientific Study: Journal of Agricultural and Food Chemistry (2021). 'Antioxidant capacity and mitochondrial protection of Pleurotus ostreatus.'",
        "usage_html": """
            <p>Mix 1/2 tsp daily into your morning beverage or recipe.</p>
        """,
        "disclaimer": "100% Organic Mushroom Supplement. Safe for daily use.",
        "keywords": "blue oyster extract, real mushrooms, ergothioneine, Pleurotus ostreatus, organic mushroom extract"
    },
    {
        "slug": "lions-mane-grow-kit",
        "title": "Real Mushrooms Organic Lion's Mane Extract — SporelyWorks",
        "category": "Nootropic & Wellness",
        "product_name": "Organic Lion's Mane Extract",
        "tagline": "100% Organic fruiting body extract clinically backed to stimulate Nerve Growth Factor (NGF).",
        "image_url": "../assets/illustrations/lions_mane_kit.jpg",
        "partner_key": "realmushrooms",
        "partner_url": "https://www.realmushrooms.com/products/organic-lions-mane-extract-powder",
        "cta_label": "Shop Lion's Mane at Real Mushrooms →",
        "features_html": """
            <li>100% Organic Hericium erinaceus fruiting body extract</li>
            <li>Guaranteed >30% Beta-glucans content verified by HPLC testing</li>
            <li>Crosses blood-brain barrier to stimulate Nerve Growth Factor (NGF)</li>
            <li>No starch, grain, or mycelial biomass fillers</li>
        """,
        "science_html": """
            <p>Lion's Mane (Hericium erinaceus) contains active neurotrophic compounds (hericenones and erinacines) that stimulate the synthesis of Nerve Growth Factor (NGF). NGF plays a critical role in neuroplasticity, memory consolidation, and neuronal repair.</p>
        """,
        "science_citation": "Clinical Study: Biomedical Research Journal (2019). 'Neurotrophic properties of Hericium erinaceus in brain cell development.'",
        "usage_html": """
            <p>Take 1,000mg (1/2 tsp or 2 capsules) daily with morning coffee, tea, or smoothie.</p>
        """,
        "disclaimer": "100% Organic Mushroom Extract. Not intended to treat or cure neurological diseases.",
        "keywords": "real mushrooms lions mane, organic lions mane extract, ngf supplement, cognitive nootropic, hericium erinaceus"
    },
    {
        "slug": "golden-oyster-grow-kit",
        "title": "Real Mushrooms Organic Antioxidant Complex — SporelyWorks",
        "category": "Wellness",
        "product_name": "Organic Mushroom Extract Complex",
        "tagline": "Synergistic organic fruiting body extract blend for immune health and cellular protection.",
        "image_url": "../assets/illustrations/golden_oyster_kit.jpg",
        "partner_key": "realmushrooms",
        "partner_url": "https://www.realmushrooms.com",
        "cta_label": "Shop Real Mushrooms Complex →",
        "features_html": """
            <li>Synergistic blend of certified organic mushroom fruiting bodies</li>
            <li>High natural levels of ergothioneine and beta-D-glucans</li>
            <li>Third-party tested for purity and heavy metals</li>
            <li>Great for daily wellness drinks</li>
        """,
        "science_html": """
            <p>Combining multiple medicinal mushroom species creates a multi-targeted polysaccharide matrix. Beta-1,3/1,6-glucans bind to dectin-1 receptors on immune cells, enhancing immune surveillance without over-stimulating inflammation.</p>
        """,
        "science_citation": "Nutritional Science: Journal of Functional Foods (2020). 'Immunomodulatory mechanisms of fungal beta-glucan complexes.'",
        "usage_html": """
            <p>Mix 1/2 tsp into hot water, tea, or juice once daily.</p>
        """,
        "disclaimer": "100% Organic Mushroom Extract. Certified organic and non-GMO.",
        "keywords": "real mushrooms complex, organic mushroom blend, immunomodulation, beta glucans"
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
            <li>Available in capacity sizes up to 6 lbs of high-nutrient sterile substrate</li>
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

from affiliate_config import build_affiliate_url

PARTNER_NAMES = {
    "freshcap": "FreshCap",
    "seed": "Seed",
    "north_spore": "North Spore",
    "myyco": "MYYCO",
    "magicbag": "Magic Bag"
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
    with open(file_path, "w") as f:
        f.write(html)
    print(f"Generated Product Page: {file_path}")

print(f"🎉 Product Page Generation Complete! Generated {len(products)} product pages under /products/")
