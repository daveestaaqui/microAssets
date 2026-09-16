#!/usr/bin/env python3
"""
SporlyWorks — Programmatic Taxonomy & Species Landing Page Generator
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIES_DIR = ROOT / "species"
SPECIES_DIR.mkdir(exist_ok=True)

SPECIES_DATA = [
    {
        "slug": "lions-mane",
        "common_name": "Lion's Mane",
        "scientific_name": "Hericium erinaceus",
        "tagline": "The Premier Neurogenesis & Cognitive Functional Mushroom",
        "image": "../assets/illustrations/lions_mane_kit.jpg",
        "taxonomy": {
            "Kingdom": "Fungi", "Division": "Basidiomycota", "Class": "Agaricomycetes",
            "Order": "Russulales", "Family": "Hericiaceae", "Genus": "Hericium", "Species": "H. erinaceus"
        },
        "cultivation": {
            "Colonization Temp": "70°F – 75°F (21°C – 24°C)",
            "Fruiting Temp": "60°F – 70°F (15°C – 21°C)",
            "Humidity Colonization": "60% – 70%",
            "Humidity Fruiting": "85% – 95%",
            "FAE Requirements": "High (5–8 room air exchanges/hr; sensitive to CO2 buildup)",
            "Optimal Substrate": "Masters Mix (50% Hardwood Sawdust / 50% Soybean Hulls)",
            "Biological Efficiency": "80% – 100% on supplemented hardwood",
            "Days to First Flush": "14 – 18 days after fruiting initiation"
        },
        "biochemistry": [
            {"compound": "Hericenones (A–H)", "source": "Fruiting Body", "mechanism": "Crosses blood-brain barrier to stimulate Nerve Growth Factor (NGF) synthesis."},
            {"compound": "Erinacines (A–I)", "source": "Cultured Mycelium", "mechanism": "Potent diterpenoid inducers of brain-derived neurotrophic factor (BDNF)."},
            {"compound": "1,3/1,6 Beta-D-Glucans", "source": "Cell Wall Matrix", "mechanism": ">25% concentration via AOAC 995.16 assay; activates macrophage phagocytosis."}
        ],
        "partner": "nootropicsdepot",
        "partner_product": "Nootropics Depot HPLC-Tested Lion's Mane 8:1 Extract",
        "partner_url": "https://nootropicsdepot.com",
        "partner_cta": "Shop Lab-Tested Lion's Mane →",
        "faq": [
            {"q": "How does Lion's Mane stimulate Nerve Growth Factor (NGF)?", "a": "Low molecular weight hericenones easily pass through the blood-brain barrier, triggering astrocytes to synthesize endogenous NGF required for hippocampal neurogenesis and synaptic plasticity."},
            {"q": "What is the best substrate for cultivating Hericium erinaceus?", "a": "The gold standard is Masters Mix: an equal 50/50 dry mass blend of coarse hardwood sawdust (oak or maple) and unpelleted soybean hulls, hydrated to 60% moisture and autoclaved at 15 PSI for 2.5 hours."}
        ]
    },
    {
        "slug": "cordyceps-militaris",
        "common_name": "Cordyceps",
        "scientific_name": "Cordyceps militaris",
        "tagline": "Cellular ATP Synthesis & High-Altitude Aerobic Endurance",
        "image": "../assets/illustrations/cordyceps_extract.jpg",
        "taxonomy": {
            "Kingdom": "Fungi", "Division": "Ascomycota", "Class": "Sordariomycetes",
            "Order": "Hypocreales", "Family": "Cordycipitaceae", "Genus": "Cordyceps", "Species": "C. militaris"
        },
        "cultivation": {
            "Colonization Temp": "68°F – 72°F (20°C – 22°C) in darkness",
            "Fruiting Temp": "62°F – 66°F (17°C – 19°C) under 12h cold-white light",
            "Humidity Colonization": "60% – 65%",
            "Humidity Fruiting": "80% – 90%",
            "FAE Requirements": "Moderate (controlled gas exchange via micron filter patch)",
            "Optimal Substrate": "Organic Brown Rice / Rye with nutrient broth (yeast, peptone, sugar)",
            "Biological Efficiency": "35% – 50% fresh harvest biomass",
            "Days to First Flush": "45 – 60 days total cycle from liquid culture inoculation"
        },
        "biochemistry": [
            {"compound": "Cordycepin (3'-deoxyadenosine)", "source": "Stroma (Fruiting Body)", "mechanism": "Adenosine analog that elevates cellular ATP production and modulates RNA synthesis."},
            {"compound": "Adenosine", "source": "Full Spectrum", "mechanism": "Supports coronary vasodilation and cellular energy transfer."},
            {"compound": "Cordycepic Acid (D-mannitol)", "source": "Fruiting Body", "mechanism": "Osmotic diuretic and metabolic scavenger supporting respiratory function."}
        ],
        "partner": "nootropicsdepot",
        "partner_product": "Nootropics Depot HPLC-Standardized Cordyceps militaris",
        "partner_url": "https://nootropicsdepot.com",
        "partner_cta": "Shop Standardized Cordyceps →",
        "faq": [
            {"q": "How does cordycepin enhance athletic endurance?", "a": "Cordycepin structurally mimics adenosine, accelerating mitochondrial phosphorylation and elevating cellular ATP reserves while facilitating oxygen extraction in peripheral tissues."},
            {"q": "Can Cordyceps militaris be cultivated vegetatively without insects?", "a": "Yes. Modern scientific mycology cultivates Cordyceps militaris on organic enriched grain broths, producing cordycepin levels significantly higher than wild insect-harvested Ophiocordyceps sinensis."}
        ]
    },
    {
        "slug": "reishi",
        "common_name": "Reishi (Lingzhi)",
        "scientific_name": "Ganoderma lucidum",
        "tagline": "Adaptogenic Longevity, Ganoderic Acids & Delta Sleep Architecture",
        "image": "../assets/illustrations/reishi_extract.jpg",
        "taxonomy": {
            "Kingdom": "Fungi", "Division": "Basidiomycota", "Class": "Agaricomycetes",
            "Order": "Polyporales", "Family": "Ganodermataceae", "Genus": "Ganoderma", "Species": "G. lucidum"
        },
        "cultivation": {
            "Colonization Temp": "75°F – 80°F (24°C – 27°C)",
            "Fruiting Temp": "70°F – 78°F (21°C – 26°C)",
            "Humidity Colonization": "65% – 70%",
            "Humidity Fruiting": "85% – 95% (conk vs antler morphology governed by CO2)",
            "FAE Requirements": "Low FAE for antlers (>2000 ppm CO2); High FAE for broad conks",
            "Optimal Substrate": "Supplemented Oak Sawdust with 15% wheat bran",
            "Biological Efficiency": "30% – 50% dry woody biomass",
            "Days to First Flush": "30 – 45 days after antler initiation"
        },
        "biochemistry": [
            {"compound": "Ganoderic Acids (A, B, C, D)", "source": "Fruiting Body / Triterpenoids", "mechanism": "Binds central GABA-A receptors, modulating delta sleep and reducing cortisol."},
            {"compound": "1,3/1,6 Beta-D-Glucans", "source": "Chitin Matrix", "mechanism": "Activates natural killer (NK) cells and cytokine signaling."},
            {"compound": "Sterols (Ergosterol)", "source": "Cell Membrane", "mechanism": "Biological precursor to vitamin D2 with immunomodulatory properties."}
        ],
        "partner": "freshcap",
        "partner_product": "FreshCap 100% Organic Reishi Fruiting Body Extract",
        "partner_url": "https://freshcap.com",
        "partner_cta": "Shop Organic Reishi Extract →",
        "faq": [
            {"q": "How do reishi triterpenoids improve deep sleep?", "a": "Ganoderic acids interact directly with GABAergic neuro-pathways in the central nervous system, calming autonomic nervous arousal and significantly increasing deep slow-wave delta sleep cycles."},
            {"q": "What determines whether Reishi grows as antlers or conks?", "a": "Carbon dioxide concentration. In elevated CO2 environments (>2000 ppm), the fungus grows elongated 'antler' stipes. Introducing high fresh air exchange (FAE) triggers horizontal conk cap expansion."}
        ]
    },
    {
        "slug": "king-trumpet",
        "common_name": "King Trumpet",
        "scientific_name": "Pleurotus eryngii",
        "tagline": "Culinary Excellence & High-Density Ergothioneine Antioxidant Source",
        "image": "../assets/illustrations/grow_kits.jpg",
        "taxonomy": {
            "Kingdom": "Fungi", "Division": "Basidiomycota", "Class": "Agaricomycetes",
            "Order": "Agaricales", "Family": "Pleurotaceae", "Genus": "Pleurotus", "Species": "P. eryngii"
        },
        "cultivation": {
            "Colonization Temp": "72°F – 76°F (22°C – 24°C)",
            "Fruiting Temp": "58°F – 64°F (14°C – 18°C) — requires cool fruiting drop",
            "Humidity Colonization": "60% – 65%",
            "Humidity Fruiting": "85% – 90%",
            "FAE Requirements": "Carefully tuned: high CO2 (1500–2000 ppm) develops thick meaty stems",
            "Optimal Substrate": "Hardwood sawdust supplemented with 20% wheat bran or soy hulls",
            "Biological Efficiency": "70% – 90% fresh mushroom yield",
            "Days to First Flush": "18 – 22 days following temperature drop"
        },
        "biochemistry": [
            {"compound": "L-Ergothioneine", "source": "Full Fruiting Body", "mechanism": "Master intracellular antioxidant with dedicated human cellular transporter (OCTN1)."},
            {"compound": "Lovastatin (Mevinolin)", "source": "Mycelium & Cap", "mechanism": "Naturally occurring HMG-CoA reductase inhibitor supporting lipid metabolism."},
            {"compound": "Pleurotus Polysaccharides", "source": "Cell Wall", "mechanism": "Supports macrophage activation and gut microbiome diversity."}
        ],
        "partner": "magicbag",
        "partner_product": "Magic Bag Pre-Sterilized All-In-One Substrate Bags",
        "partner_url": "https://www.magicbag.co",
        "partner_cta": "Shop All-In-One Grow Bags →",
        "faq": [
            {"q": "Why does King Trumpet require a temperature drop to fruit?", "a": "Pleurotus eryngii is a cool-season Mediterranean species whose pinning mechanism is biologically governed by an environmental temperature reduction from 75°F down to 58°F–62°F."},
            {"q": "What makes King Trumpet mushrooms rich in ergothioneine?", "a": "King Trumpets are among the richest dietary sources of L-ergothioneine, an antioxidant that cells absorb through the specialized OCTN1 transporter to shield mitochondrial DNA from oxidative stress."}
        ]
    },
    {
        "slug": "psilocybe-natalensis",
        "common_name": "Psilocybe natalensis",
        "scientific_name": "Psilocybe natalensis",
        "tagline": "Taxonomy, Microscopy & Cytological Hyphal Resilience",
        "image": "../assets/illustrations/natalensis_spores.jpg",
        "taxonomy": {
            "Kingdom": "Fungi", "Division": "Basidiomycota", "Class": "Agaricomycetes",
            "Order": "Agaricales", "Family": "Hymenogastraceae", "Genus": "Psilocybe", "Species": "P. natalensis"
        },
        "cultivation": {
            "Colonization Temp": "75°F – 80°F (24°C – 27°C) for laboratory petri dish research",
            "Fruiting Temp": "Federally restricted — studied strictly under microscopy slides",
            "Humidity Colonization": "60% – 70% in sterile laboratory environment",
            "Humidity Fruiting": "N/A — Taxonomy & microscopy study only",
            "FAE Requirements": "High hyphal septation rates under laboratory observation",
            "Optimal Substrate": "Agar media (MEA, PDA) for cytological and genetic isolation",
            "Biological Efficiency": "Extreme rhizomorphic vigor documented in academic literature",
            "Days to First Flush": "Documented high vegetative colonization velocity"
        },
        "biochemistry": [
            {"compound": "Rhizomorphic Secondary Metabolites", "source": "Vegetative Mycelium", "mechanism": "Aggressive competitive inhibition against Pseudomonas and Trichoderma mold spores."},
            {"compound": "Laccase & Cellulase Enzymes", "source": "Secreted Matrix", "mechanism": "Rapid degradation of complex lignocellulosic bonds under magnification."},
            {"compound": "Spore Pigmentation Matrix", "source": "Microscopy Spores", "mechanism": "Dark purple-brown elliptical spores with distinct apical germ pore."}
        ],
        "partner": "myyco",
        "partner_product": "MYYCO Isolated Psilocybe natalensis Liquid Culture Syringe",
        "partner_url": "https://myyco.com/shop-microscopy-liquid-culture/",
        "partner_cta": "Shop MYYCO Microscopy Genetics →",
        "faq": [
            {"q": "How does Psilocybe natalensis differ cytologically from Psilocybe cubensis?", "a": "Under 400x–1000x magnification, P. natalensis exhibits accelerated septal wall formation, wider hyphal branching angles (45°–60°), and denser cord-like rhizomorphic growth with elevated natural contamination resistance."},
            {"q": "What are the legal compliance standards for spore syringes?", "a": "Spore syringes and isolated liquid cultures of active species are provided exclusively for scientific laboratory research, taxonomy, and microscopy. Inoculation into substrate is subject to state and federal statutes. Shipping restrictions apply to CA, GA, and ID."}
        ]
    },
    {
        "slug": "blue-oyster",
        "common_name": "Blue Oyster",
        "scientific_name": "Pleurotus ostreatus",
        "tagline": "Fastest Mycelial Colonization & 100%+ Biological Efficiency",
        "image": "../assets/illustrations/blue_oyster_kit.jpg",
        "taxonomy": {
            "Kingdom": "Fungi", "Division": "Basidiomycota", "Class": "Agaricomycetes",
            "Order": "Agaricales", "Family": "Pleurotaceae", "Genus": "Pleurotus", "Species": "P. ostreatus"
        },
        "cultivation": {
            "Colonization Temp": "70°F – 75°F (21°C – 24°C)",
            "Fruiting Temp": "55°F – 68°F (13°C – 20°C)",
            "Humidity Colonization": "60% – 65%",
            "Humidity Fruiting": "85% – 95%",
            "FAE Requirements": "Extremely High (6–10 room exchanges/hr; low FAE causes long stems)",
            "Optimal Substrate": "Pasteurized Straw, Hardwood Sawdust, or All-In-One Bags",
            "Biological Efficiency": "90% – 125% fresh yield",
            "Days to First Flush": "7 – 10 days after slash initiation"
        },
        "biochemistry": [
            {"compound": "Pleurotus Beta-Glucans", "source": "Caps & Gills", "mechanism": "Supports cholesterol reduction and activates cellular immune defenses."},
            {"compound": "Statins (Lovastatin)", "source": "Mycelium", "mechanism": "Natural regulation of lipid synthase pathways."},
            {"compound": "Antioxidant Phenolics", "source": "Pigmented Cuticle", "mechanism": "Blue pigments provide protective radical-scavenging activity."}
        ],
        "partner": "magicbag",
        "partner_product": "Magic Bag Blue Oyster Grow Kit",
        "partner_url": "https://www.magicbag.co",
        "partner_cta": "Shop Blue Oyster Kit →",
        "faq": [
            {"q": "Why do oyster mushrooms produce long stems with tiny caps?", "a": "This is a direct symptom of CO2 buildup and insufficient fresh air exchange (FAE). Oyster mushrooms require brisk air movement to trigger broad cap development."},
            {"q": "What is the expected biological efficiency of Pleurotus ostreatus?", "a": "Oyster mushrooms are among the most efficient biological converters known, consistently achieving 100% to 125% Biological Efficiency on pasteurized straw and supplemented sawdust."}
        ]
    },
    {
        "slug": "golden-oyster",
        "common_name": "Golden Oyster",
        "scientific_name": "Pleurotus citrinopileatus",
        "tagline": "Warm-Weather Prolific Fruiter with Vibrant Flavonoid Pigmentation",
        "image": "../assets/illustrations/golden_oyster_kit.jpg",
        "taxonomy": {
            "Kingdom": "Fungi", "Division": "Basidiomycota", "Class": "Agaricomycetes",
            "Order": "Agaricales", "Family": "Pleurotaceae", "Genus": "Pleurotus", "Species": "P. citrinopileatus"
        },
        "cultivation": {
            "Colonization Temp": "75°F – 82°F (24°C – 28°C)",
            "Fruiting Temp": "68°F – 78°F (20°C – 26°C)",
            "Humidity Colonization": "60% – 65%",
            "Humidity Fruiting": "85% – 90%",
            "FAE Requirements": "High (5–8 fresh air exchanges per hour)",
            "Optimal Substrate": "Hardwood sawdust or agricultural straw",
            "Biological Efficiency": "85% – 110% fresh yield",
            "Days to First Flush": "9 – 12 days"
        },
        "biochemistry": [
            {"compound": "Golden Carotenoid/Flavonoid Matrix", "source": "Bright Yellow Caps", "mechanism": "Potent free radical scavenging in biological tissues."},
            {"compound": "Polysaccharide-Protein Complexes", "source": "Fruiting Body", "mechanism": "Stimulates T-lymphocyte proliferation and humoral immunity."}
        ],
        "partner": "magicbag",
        "partner_product": "Magic Bag Golden Oyster Grow Kit",
        "partner_url": "https://www.magicbag.co",
        "partner_cta": "Shop Golden Oyster Kit →",
        "faq": [
            {"q": "Can Golden Oyster mushrooms grow in hot summer conditions?", "a": "Yes. Pleurotus citrinopileatus thrives in warmer ambient temperatures between 70°F and 80°F, making it the premier warm-weather gourmet species."}
        ]
    },
    {
        "slug": "shiitake",
        "common_name": "Shiitake",
        "scientific_name": "Lentinula edodes",
        "tagline": "Traditional Lignocellulose Decayer Rich in Lentinan & AHCC Precursors",
        "image": "../assets/illustrations/grow_kits.jpg",
        "taxonomy": {
            "Kingdom": "Fungi", "Division": "Basidiomycota", "Class": "Agaricomycetes",
            "Order": "Agaricales", "Family": "Omphalotaceae", "Genus": "Lentinula", "Species": "L. edodes"
        },
        "cultivation": {
            "Colonization Temp": "72°F – 78°F (22°C – 25°C) — requires 8–12 week browning cycle",
            "Fruiting Temp": "55°F – 65°F (13°C – 18°C) cold shock required",
            "Humidity Colonization": "60%",
            "Humidity Fruiting": "80% – 85%",
            "FAE Requirements": "Moderate to High",
            "Optimal Substrate": "Oak Sawdust with 20% wheat bran (supplemented hardwood)",
            "Biological Efficiency": "60% – 80% fresh yield",
            "Days to First Flush": "12 – 16 days after 24h cold soak immersion"
        },
        "biochemistry": [
            {"compound": "Lentinan", "source": "Fruiting Body", "mechanism": "High-molecular weight 1,3 beta-glucan used clinically in Japan as an approved biological response modifier."},
            {"compound": "Eritadenine", "source": "Cap & Stipe", "mechanism": "Accelerates blood cholesterol clearance and supports vascular elasticity."}
        ],
        "partner": "nootropicsdepot",
        "partner_product": "Nootropics Depot Lab-Tested Fungal Extracts",
        "partner_url": "https://nootropicsdepot.com",
        "partner_cta": "Shop Lab-Tested Extracts →",
        "faq": [
            {"q": "Why does Shiitake mycelium turn dark brown before fruiting?", "a": "Shiitake undergoes a distinct 'popcorning' and 'browning' phase where outer mycelial cells melanize. This protective pseudo-bark layer seals moisture in the block and signals physiological readiness for fruiting."},
            {"q": "What is the biological role of Lentinan?", "a": "Lentinan is a purified 1,3 beta-D-glucan polysaccharide that stimulates helper T-cells and macrophage cytotoxicity, extensively validated in peer-reviewed clinical literature."}
        ]
    }
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — SporlyWorks</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{canonical}">
    <link rel="icon" type="image/x-icon" href="../assets/favicon.ico">
    <meta property="og:title" content="{title} — SporlyWorks">
    <meta property="og:description" content="{description}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{og_image}">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Serif+Display&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../style.css?v=1200">
    <script type="application/ld+json">
{schema_json}
    </script>
    <style>
        .species-page-container {{ max-width: 940px; margin: 130px auto 70px; padding: 0 24px; }}
        .species-hero-card {{ background: rgba(255, 255, 255, 0.9); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 44px; box-shadow: 0 12px 48px rgba(44, 36, 24, 0.04); margin-bottom: 40px; display: flex; gap: 36px; align-items: center; }}
        @media (max-width: 768px) {{ .species-hero-card {{ flex-direction: column; text-align: center; }} }}
        .species-hero-img {{ width: 280px; height: 280px; object-fit: cover; border-radius: var(--radius-md); border: 1px solid var(--border-color); background: rgba(245, 240, 232, 0.5); flex-shrink: 0; }}
        .species-title {{ font-family: 'DM Serif Display', Georgia, serif; font-size: 38px; color: var(--green-dark); margin-bottom: 6px; }}
        .species-sci {{ font-family: 'Cormorant Garamond', Georgia, serif; font-style: italic; font-size: 22px; color: var(--gold-dark); margin-bottom: 12px; }}
        .species-tagline {{ font-size: 16.5px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 24px; }}
        .data-table-wrap {{ background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-md); overflow: hidden; margin-bottom: 36px; box-shadow: 0 2px 12px rgba(0,0,0,0.02); }}
        .data-table {{ width: 100%; border-collapse: collapse; font-size: 14.5px; }}
        .data-table th, .data-table td {{ padding: 14px 18px; border-bottom: 1px solid var(--border-color); text-align: left; }}
        .data-table th {{ background: rgba(27, 138, 90, 0.06); color: var(--green-dark); font-weight: 700; width: 35%; }}
        .data-table tr:last-child th, .data-table tr:last-child td {{ border-bottom: none; }}
        .section-header {{ font-family: 'DM Serif Display', serif; font-size: 26px; color: var(--green-dark); margin: 36px 0 16px; border-bottom: 2px solid var(--gold-light); padding-bottom: 8px; }}
        .cta-banner {{ background: linear-gradient(135deg, rgba(27, 138, 90, 0.08), rgba(196, 151, 59, 0.08)); border: 1px solid rgba(27, 138, 90, 0.2); border-radius: var(--radius-md); padding: 32px; text-align: center; margin: 40px 0; }}
        .btn-cta {{ display: inline-block; background: linear-gradient(135deg, var(--green-light), var(--green)); color: #ffffff !important; padding: 14px 32px; border-radius: var(--radius-pill); text-decoration: none; font-weight: 700; font-size: 15.5px; box-shadow: 0 4px 14px rgba(11, 74, 46, 0.2); transition: all 0.2s ease; margin-top: 14px; }}
        .btn-cta:hover {{ transform: translateY(-2px); }}
        .faq-item {{ background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 20px; margin-bottom: 14px; }}
        .faq-q {{ font-weight: 700; color: var(--green-dark); font-size: 16px; margin-bottom: 8px; }}
        .faq-a {{ color: var(--text-secondary); font-size: 14.5px; line-height: 1.6; margin: 0; }}
        .legal-notice {{ font-size: 12.5px; color: var(--text-muted); line-height: 1.6; margin-top: 36px; padding: 16px; background: rgba(245, 240, 232, 0.5); border-radius: var(--radius-sm); border: 1px solid var(--border-color); }}
    </style>
</head>
<body>
    <header class="internal-header">
        <div class="header-logo-centered">
            <a href="../index.html" class="header-brand-link">
                <img src="../assets/logo-nav.png?v=960" alt="SporlyWorks" class="header-logo-img">
                <span class="header-wordmark">SPORLYWORKS</span>
            </a>
        </div>
        <nav class="header-nav-centered">
            <div class="nav-links-row">
                <a href="../index.html">Home</a>
                <a href="../products.html">Shop Products</a>
                <a href="../tools/yield-estimator.html">Yield Calculator</a>
                <a href="../tools/substrate-calculator.html">Substrate Calculator</a>
                <a href="../blog/index.html">Research Blog</a>
            </div>
        </nav>
    </header>
    <main class="species-page-container">
        <div class="species-hero-card">
            <img src="{image}" alt="{common_name}" class="species-hero-img">
            <div>
                <h1 class="species-title">{common_name}</h1>
                <div class="species-sci">{scientific_name}</div>
                <p class="species-tagline">{tagline}</p>
                <a href="{partner_url}" data-partner="{partner}" class="btn-cta" target="_blank" rel="noopener sponsored">{partner_cta}</a>
            </div>
        </div>
        <h2 class="section-header">1. Taxonomic & Scientific Classification</h2>
        <div class="data-table-wrap">
            <table class="data-table">
                <tbody>{tax_rows}</tbody>
            </table>
        </div>
        <h2 class="section-header">2. Optimal Cultivation Parameters</h2>
        <div class="data-table-wrap">
            <table class="data-table">
                <tbody>{cult_rows}</tbody>
            </table>
        </div>
        <h2 class="section-header">3. Analytical Chemistry & HPLC Biochemical Assay</h2>
        <div class="data-table-wrap">
            <table class="data-table">
                <thead>
                    <tr><th>Active Compound</th><th>Botanical Source</th><th>Physiological Mechanism</th></tr>
                </thead>
                <tbody>{bio_rows}</tbody>
            </table>
        </div>
        <div class="cta-banner">
            <h3 style="font-family:'DM Serif Display',serif; color:var(--green-dark); font-size:24px; margin-bottom:8px;">Certified Laboratory Genetics & Verified Formulations</h3>
            <p style="color:var(--text-secondary); max-width:600px; margin:0 auto 16px; font-size:15px;">Access sterile liquid culture syringes and analytical fruiting body extracts tested via HPLC/HPTLC.</p>
            <a href="{partner_url}" data-partner="{partner}" class="btn-cta" target="_blank" rel="noopener sponsored">{partner_cta}</a>
        </div>
        <h2 class="section-header">4. Scientific Questions & Empirical Protocols</h2>
        {faq_rows}
        <div class="legal-notice">
            <strong>Legal & Analytical Disclaimer:</strong> SporlyWorks participates in partner programs and may earn commissions on qualified referrals at no cost to you. Dietary supplements and extracts are not intended to diagnose, treat, cure, or prevent any disease. Spore solutions and liquid cultures of active species are provided strictly for taxonomy and microscopy research.
        </div>
    </main>
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
                    <a href="../tools/substrate-calculator.html">Substrate Calculator</a>
                    <a href="../tools/wellness-stack-builder.html">Stack Builder</a>
                    <a href="../tools/diagnostics.html">Diagnostics Guide</a>
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
    <script src="../assets/affiliate-manager.js"></script>
    <script src="../assets/page-transitions.js"></script>
</body>
</html>"""

def generate():
    for sp in SPECIES_DATA:
        slug = sp["slug"]
        title = f"{sp['common_name']} ({sp['scientific_name']}) Taxonomy & Cultivation Parameters"
        description = f"Comprehensive scientific guide to {sp['common_name']} ({sp['scientific_name']}). Verified cultivation parameters, biological efficiency, active compounds, and HPLC assays."
        canonical = f"https://sporlyworks.com/species/{slug}.html"
        og_image = f"https://sporlyworks.com/{sp['image'].lstrip('../')}"

        schema_ld = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Article",
                    "@id": f"{canonical}#article",
                    "headline": title,
                    "description": description,
                    "image": og_image,
                    "author": {"@type": "Organization", "name": "SporlyWorks Scientific Advisory Board"},
                    "publisher": {"@type": "Organization", "name": "SporlyWorks", "logo": {"@type": "ImageObject", "url": "https://sporlyworks.com/assets/logo.png"}}
                },
                {
                    "@type": "Product",
                    "@id": f"{canonical}#product",
                    "name": sp["partner_product"],
                    "description": sp["tagline"],
                    "brand": {"@type": "Brand", "name": sp["partner"].capitalize()},
                    "offers": {"@type": "Offer", "url": sp["partner_url"], "priceCurrency": "USD", "availability": "https://schema.org/InStock"}
                },
                {
                    "@type": "FAQPage",
                    "@id": f"{canonical}#faq",
                    "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in sp["faq"]]
                }
            ]
        }

        tax_rows = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in sp["taxonomy"].items())
        cult_rows = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in sp["cultivation"].items())
        bio_rows = "".join(f"<tr><th>{c['compound']}</th><td>{c['source']}</td><td>{c['mechanism']}</td></tr>" for c in sp["biochemistry"])
        faq_rows = "".join(f'<div class="faq-item"><div class="faq-q">{item["q"]}</div><p class="faq-a">{item["a"]}</p></div>' for item in sp["faq"])

        html_out = HTML_TEMPLATE.format(
            title=title,
            description=description,
            canonical=canonical,
            og_image=og_image,
            schema_json=json.dumps(schema_ld, indent=2),
            image=sp["image"],
            common_name=sp["common_name"],
            scientific_name=sp["scientific_name"],
            tagline=sp["tagline"],
            partner=sp["partner"],
            partner_url=sp["partner_url"],
            partner_cta=sp["partner_cta"],
            tax_rows=tax_rows,
            cult_rows=cult_rows,
            bio_rows=bio_rows,
            faq_rows=faq_rows
        )

        out_file = SPECIES_DIR / f"{slug}.html"
        out_file.write_text(html_out.strip() + "\n", encoding="utf-8")
        print(f"Generated {out_file.relative_to(ROOT)}")

if __name__ == "__main__":
    generate()
