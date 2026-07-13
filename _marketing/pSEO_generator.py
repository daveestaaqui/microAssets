#!/usr/bin/env python3
import os
import json

# Define the guides directory
BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
GUIDES_DIR = os.path.join(BASE_DIR, "guides")
os.makedirs(GUIDES_DIR, exist_ok=True)

# Define templates and common assets
STYLE_PATH = "../style.css?v=910"
FAVICON_PATH = "../assets/favicon.ico"
NAV_ICON = "../assets/logo-nav.png?v=908"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} — SporlyWorks Mycology & Wellness Guides</title>
    <meta name="description" content="{{description}}">
    <meta name="keywords" content="{{keywords}}">
    <link rel="canonical" href="https://sporlyworks.com/guides/{{slug}}.html">
    <link rel="icon" type="image/x-icon" href="{{favicon}}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Serif+Display&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{style_path}}">
    <style>
        .guide-body {{
            max-width: 800px;
            margin: 120px auto 80px;
            padding: 0 24px;
        }}
        .guide-header {{
            text-align: center;
            margin-bottom: 48px;
        }}
        .guide-title {{
            font-size: 42px;
            color: var(--green-dark);
            margin-bottom: 16px;
            font-family: 'DM Serif Display', Georgia, serif;
        }}
        .guide-meta {{
            color: var(--text-muted);
            font-size: 14px;
            margin-bottom: 24px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .guide-intro {{
            font-size: 18px;
            line-height: 1.8;
            color: var(--text-secondary);
            font-style: italic;
            margin-bottom: 32px;
            border-bottom: 1px solid var(--glass-border);
            padding-bottom: 32px;
        }}
        .guide-content h2 {{
            font-size: 28px;
            color: var(--green);
            margin: 40px 0 16px;
            font-family: 'DM Serif Display', Georgia, serif;
        }}
        .guide-content p {{
            font-size: 16px;
            line-height: 1.7;
            color: var(--text-primary);
            margin-bottom: 24px;
        }}
        .guide-content ul, .guide-content ol {{
            margin-left: 24px;
            margin-bottom: 24px;
            color: var(--text-primary);
        }}
        .guide-content li {{
            margin-bottom: 8px;
        }}
        .guide-takeaway {{
            background: var(--bg-surface-elevated);
            border-left: 4px solid var(--gold);
            padding: 24px;
            border-radius: var(--radius-sm);
            margin: 32px 0;
            box-shadow: var(--shadow-soft);
        }}
        .guide-takeaway p {{
            margin: 0;
            font-size: 15px;
            color: var(--text-secondary);
            line-height: 1.6;
        }}
        .partner-cta-box {{
            background: linear-gradient(135deg, var(--green-dark), #03150e);
            color: var(--text-on-dark);
            padding: 40px;
            border-radius: var(--radius-md);
            margin-top: 48px;
            text-align: center;
            border: 1px solid var(--gold-dark);
        }}
        .partner-cta-box h3 {{
            color: var(--gold-light);
            font-size: 24px;
            margin-bottom: 12px;
        }}
        .partner-cta-box p {{
            color: var(--text-on-dark);
            opacity: 0.85;
            font-size: 15px;
            max-width: 600px;
            margin: 0 auto 24px;
        }}
        .partner-cta-btn {{
            display: inline-block;
            background: linear-gradient(135deg, var(--gold-light), var(--gold));
            color: #000;
            padding: 12px 32px;
            border-radius: var(--radius-pill);
            text-decoration: none;
            font-weight: 700;
            transition: all 0.3s;
        }}
        .partner-cta-btn:hover {{
            transform: scale(1.03);
            box-shadow: 0 0 20px rgba(196, 151, 59, 0.4);
        }}
    </style>
</head>
<body>

    <!-- ═══ NAVIGATION ═══ -->
    <nav id="mainNav" class="scrolled">
        <div class="nav-inner">
            <a href="../index.html" class="nav-brand">
                <img src="{nav_icon}" alt="SporlyWorks" class="nav-icon">
                <span class="nav-wordmark">SPORLYWORKS</span>
            </a>
            <div class="nav-menu-row">
                <div class="nav-links">
                    <a href="../products.html">Products</a>
                    <a href="../tools/yield-estimator.html">Yield Estimator</a>
                    <a href="../tools/wellness-stack-builder.html">Stack Builder</a>
                    <a href="../tools/diagnostics.html">Diagnostics</a>
                    <a href="../tools/substrate-calculator.html">Substrate Calculator</a>
                    <a href="../blog/index.html" class="active">Blog</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- ═══ MAIN CONTENT ═══ -->
    <main class="guide-body">
        <article class="guide-card">
            <header class="guide-header">
                <div class="guide-meta">Category: {category} · Technical Guide</div>
                <h1 class="guide-title">{heading}</h1>
                {hero_image_tag}
            </header>
            
            <p class="guide-intro">{intro}</p>
            
            <div class="guide-content">
                {content}
            </div>

            <div class="guide-takeaway">
                <p><strong>Clinical & Mycology Note:</strong> {takeaway}</p>
            </div>

            <div class="partner-cta-box">
                <h3>Ready to Take the Next Step?</h3>
                <p>{cta_text}</p>
                <a href="{partner_url}" id="cta-{partner_key}" class="partner-cta-btn" target="_blank" rel="noopener">{partner_cta}</a>
            </div>
        </article>
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
    // Load affiliate config dynamically for this deep page
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
        .catch(() => console.log('Config fetch skipped - using static default'));
    </script>
<script src="../assets/page-transitions.js"></script>
</body>
</html>
"""

# Guide definitions
guides = [
    {
        "slug": "lions-mane-cognitive-wellness",
        "title": "Lion's Mane Mushroom Guide: Cognitive Health & NGF Stimulation",
        "category": "Supplements",
        "heading": "The Scientific Case for Lion's Mane in Cognitive Wellness",
        "intro": "Hericium erinaceus, commonly known as Lion's Mane, is a culinary and medicinal mushroom with unique neurological properties. Emerging research points to its ability to stimulate Nerve Growth Factor (NGF) and actively support memory and focus.",
        "content": """
            <h2>What is Nerve Growth Factor (NGF)?</h2>
            <p>Nerve Growth Factor is a small secreted protein that is essential for the growth, maintenance, and survival of certain neurons. As we age, or due to chronic oxidative stress, our natural production of NGF decreases, leading to cognitive fatigue, memory lapses, and slower neural connectivity.</p>
            <p>Traditional remedies and synthetic supplements often fail to cross the blood-brain barrier. However, Lion's Mane contains two families of active compounds—hericenones (found in the fruiting body) and erinacines (found in the mycelium)—that are small enough to pass the blood-brain barrier and directly stimulate NGF synthesis.</p>

            <h2>Whole Fruiting Body vs. Mycelium on Grain</h2>
            <p>When selecting a supplement, purity is paramount. Many mass-market brands grow mushroom mycelium on grains (such as oats or rice) and grind the entire substrate into powder. This results in a product that is up to 70% starch and only 30% active compounds.</p>
            <p>For therapeutic effects, clinical studies rely on whole-fruiting body extracts. The fruiting body contains the highest concentration of beta-glucans—polysaccharides that interact directly with the immune and nervous systems to yield tangible health improvements.</p>

            <h2>How to Incorporate Lion's Mane Into Your Daily Stack</h2>
            <p>For optimal results, consume 1,000 mg of organic Lion's Mane extract powder daily. It is soluble in hot water, making it a perfect addition to morning coffee, tea, or protein smoothies. Most users report increased focus, mental clarity, and improved recall after 2–3 weeks of consistent daily usage.</p>
        """,
        "takeaway": "Always look for certified organic, 100% fruiting body extracts with verified beta-glucan levels to ensure you are receiving the active ingredients necessary for neurogenesis.",
        "partner_key": "real_mushrooms",
        "partner_url": "https://www.realmushrooms.com",
        "cta_text": "Get the highest-purity, USDA Organic Lion's Mane extract powder directly from our trusted scientific partner, Real Mushrooms.",
        "partner_cta": "Shop Lion's Mane Extract at Real Mushrooms →",
        "keywords": "lions mane supplement, neurogenesis NGF, organic mushroom extract, brain health supplements, focus memory"
    },
    {
        "slug": "grow-kit-biological-efficiency",
        "title": "Maximizing Mushroom Grow Kit Yield: The Science of Biological Efficiency",
        "category": "Cultivation",
        "heading": "Maximizing Yields: The Science Behind Pre-Colonized Grow Blocks",
        "intro": "Starting a mushroom crop from scratch requires months of sterile lab work, pressure cookers, and high contamination risks. Pre-colonized mushroom grow blocks solve these barriers, utilizing fully established mycelial networks to guarantee massive gourmet harvests.",
        "content": """
            <h2>Understanding Biological Efficiency (BE)</h2>
            <p>In mushroom cultivation, Biological Efficiency (BE) is the ratio of fresh mushroom weight harvested to the dry weight of the substrate. For instance, if a 5 lb block (at 60% moisture, meaning 2 lbs dry weight) produces 2 lbs of fresh mushrooms, it has achieved 100% Biological Efficiency.</p>
            <p>Gourmet wood-loving species like Oyster (Pleurotus) and Lion's Mane (Hericium) are highly efficient bio-converters. However, to maximize this ratio, the substrate must be packed with the perfect blend of cellulose, lignin, and supplementary nitrogen (often oak sawdust supplemented with wheat bran).</p>

            <h2>Why Pre-Colonization Matters</h2>
            <p>The most vulnerable stage of mycology is inoculation and colonization. Molds, bacteria, and wild yeast grow much faster than mushroom mycelium. If a single spore enters the substrate before the mycelium dominates, it will ruin the block.</p>
            <p>Pre-colonized kits bypass this entire risk. Mycologists inoculate sterile sawdust blocks in cleanrooms using HEPA laminar flow hoods. By the time the kit arrives at your home, the mycelium has completely colonized the substrate. Because it has established absolute dominance, the risk of contamination is virtually zero, and the block is primed to channel all its energy into fruiting.</p>

            <h2>Tips for Massive Harvests</h2>
            <p>To get the highest possible yield from your grow kit:</p>
            <ul>
                <li><strong>Humidity:</strong> Spray the slit 2-3 times daily. Mushrooms are 90% water and require constant relative humidity above 85%.</li>
                <li><strong>Light:</strong> Mushrooms need indirect ambient light to trigger pin development and develop rich color (they do not photosynthesize, but light acts as an environmental signal).</li>
                <li><strong>Air Flow:</strong> Mushrooms breathe oxygen and release CO2. Ensure they are in a well-ventilated area so they don't grow long, leggy stems.</li>
            </ul>
        """,
        "takeaway": "Starting with pre-colonized blocks (like North Spore kits) guarantees a robust first flush and lets you harvest gourmet Oyster or Lion's Mane mushrooms in just 10-14 days.",
        "partner_key": "north_spore",
        "partner_url": "https://northspore.com",
        "cta_text": "Choose from Blue Oyster, Lion's Mane, and Golden Oyster grow kits, backed by a 100% grow guarantee from North Spore.",
        "partner_cta": "Browse Grow Kits at North Spore →",
        "keywords": "mushroom grow kit, biological efficiency mycology, oyster mushroom cultivation, home grow block, how to grow mushrooms"
    },
    {
        "slug": "ds01-synbiotic-gut-science",
        "title": "Why Standard Probiotics Fail: The Dual-Capsule Delivery System",
        "category": "Probiotics",
        "heading": "Survivability: The Deciding Factor in Probiotic Efficacy",
        "intro": "Most probiotic supplements on store shelves never actually reach your gut. The high-acid environment of the stomach destroys live bacteria before they arrive in the colon. Here is the science of why delivery technology is just as important as the bacterial strains themselves.",
        "content": """
            <h2>The Digestive Gauntlet</h2>
            <p>Your digestive system is designed to destroy foreign microorganisms. Stomach acid, bile salts, and digestive enzymes form an aggressive barrier. While this is crucial for preventing foodborne illness, it poses a major challenge for probiotic supplements.</p>
            <p>Clinical tests show that standard capsules or probiotic yogurt lose over 90% of their viable bacteria during transit through the stomach and duodenum. If the bacteria are dead by the time they reach the colon, they cannot colonize or provide any health benefits.</p>

            <h2>ViaCap®: The Dual-Capsule Solution</h2>
            <p>To solve this survivability crisis, advanced biotech utilizes a nested delivery system. An inner capsule containing the probiotic strains is nested inside an outer capsule containing a liquid prebiotic.</p>
            <p>The outer capsule acts as a barrier, shielding the sensitive inner capsule from stomach acid. The outer layer dissolves slowly in the early small intestine, releasing the prebiotic, while the inner capsule remains intact until it reaches the lower bowel. This ensures that 100% of the active probiotic dose is delivered alive, ready to settle in the colon.</p>

            <h2>Strain-Specific Benefits</h2>
            <p>Not all bacteria are created equal. Effective probiotics are categorized by specific, clinically-studied strains rather than just broad species. For example, specific strains support gut barrier integrity, skin health, micronutrient synthesis, and immune cell training, which are essential for overall systemic wellness.</p>
        """,
        "takeaway": "To get real digestive and immune benefits, look for synbiotics that combine clinically validated bacterial strains with a multi-layered delivery system designed for survivability.",
        "partner_key": "seed",
        "partner_url": "https://seed.com",
        "cta_text": "Invest in science-backed gut health with Seed's DS-01® Daily Synbiotic, engineered with ViaCap® survivability technology.",
        "partner_cta": "Get 15% Off Your First Month of Seed →",
        "keywords": "probiotic survivability, daily synbiotic, gut microbiome health, seed probiotic, nested capsule delivery"
    }
]

# Generate each guide file
for guide in guides:
    # Determine matching illustration for guide
    hero_image = "../assets/illustrations/spores.jpg"
    if "lions-mane" in guide["slug"]:
        hero_image = "../assets/illustrations/lions_mane_kit.jpg"
    elif "grow-kit" in guide["slug"]:
        hero_image = "../assets/illustrations/grow_kits.jpg"
    elif "ds01" in guide["slug"]:
        hero_image = "../assets/illustrations/synbiotics.jpg"
        
    hero_image_tag = f'<img src="{hero_image}" alt="{guide["title"]}" class="guide-hero-img" style="width:100%; height:320px; object-fit:contain; background:var(--bg-surface-elevated); padding:16px; border-radius:var(--radius-lg); margin-top:24px; border:1px solid var(--border-color);">'

    html = PAGE_TEMPLATE.format(
        title=guide["title"],
        description=guide["intro"],
        keywords=guide["keywords"],
        slug=guide["slug"],
        favicon=FAVICON_PATH,
        style_path=STYLE_PATH,
        nav_icon=NAV_ICON,
        category=guide["category"],
        heading=guide["heading"],
        hero_image_tag=hero_image_tag,
        intro=guide["intro"],
        content=guide["content"],
        takeaway=guide["takeaway"],
        partner_key=guide["partner_key"],
        partner_url=guide["partner_url"],
        cta_text=guide["cta_text"],
        partner_cta=guide["partner_cta"]
    )
    
    file_path = os.path.join(GUIDES_DIR, f"{guide['slug']}.html")
    with open(file_path, "w") as f:
        f.write(html)
    print(f"Generated Guide: {file_path}")

print("🎉 pSEO Generation Complete! Generated 3 high-intent technical guides in /guides/")
