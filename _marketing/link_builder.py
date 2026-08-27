#!/usr/bin/env python3
"""
SporlyWorks — Automated Link Building & Content Syndication Draft Generator

Generates:
1. Web directory submission data
2. Reddit/forum post drafts with natural backlinks
3. Pinterest pin descriptions
4. Guest post pitch templates for mycology blogs
5. Weekly backlink opportunity report

All outputs are saved to _marketing/link_building_drafts/
"""

import os
import json
import datetime
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "_marketing", "link_building_drafts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SITE_URL = "https://sporlyworks.com"
SITE_NAME = "SporlyWorks"
SITE_DESCRIPTION = "Science-backed mushroom cultivation kits, certified spore genetics for microscopy research, and organic adaptogenic supplements."

# ═══════════════════════════════════════════════════════════════
# CONTENT POOLS — Rotate weekly for fresh, non-repetitive posts
# ═══════════════════════════════════════════════════════════════

BLOG_ARTICLES = [
    {"title": "Lion's Mane & Neurogenesis: How Hericenones Stimulate Nerve Growth Factor", "url": f"{SITE_URL}/blog/lions-mane-neurogenesis.html", "category": "Wellness"},
    {"title": "Cordyceps & Cellular ATP: The Science Behind Natural Energy", "url": f"{SITE_URL}/blog/cordyceps-atp-cellular-energy.html", "category": "Wellness"},
    {"title": "Reishi Triterpenes & Sleep Architecture", "url": f"{SITE_URL}/blog/reishi-triterpenes-sleep-architecture.html", "category": "Wellness"},
    {"title": "Identifying Contamination in Your Grow: Trichoderma vs Cobweb vs Healthy Mycelium", "url": f"{SITE_URL}/blog/identifying-grow-contamination.html", "category": "Cultivation"},
    {"title": "Monotub Tek: A Beginner's Guide to Bulk Cultivation", "url": f"{SITE_URL}/blog/monotub-tek-beginners-guide.html", "category": "Cultivation"},
    {"title": "Liquid Culture vs Spore Syringe: Which Is Better for Inoculation?", "url": f"{SITE_URL}/blog/liquid-culture-vs-spore-syringe.html", "category": "Cultivation"},
    {"title": "Fruiting Conditions: Mastering FAE, Humidity & Light", "url": f"{SITE_URL}/blog/fruiting-conditions-fae-humidity.html", "category": "Cultivation"},
    {"title": "Beta-Glucan Extraction Methods: Hot Water vs Dual Extract", "url": f"{SITE_URL}/blog/beta-glucan-extraction-methods.html", "category": "Wellness"},
    {"title": "Psilocybe Natalensis Genetics: Why This Species Is Special", "url": f"{SITE_URL}/blog/psilocybe-natalensis-genetics.html", "category": "Microscopy"},
    {"title": "All-In-One Grow Bag Guide: Sterile Substrate Science", "url": f"{SITE_URL}/blog/all-in-one-grow-bag-guide.html", "category": "Cultivation"},
    {"title": "Grain Spawn Preparation & Sterilization Protocols", "url": f"{SITE_URL}/blog/grain-spawn-preparation-sterilization.html", "category": "Cultivation"},
    {"title": "Synbiotics & Nutrient Absorption: How Probiotics Boost Supplement Efficacy", "url": f"{SITE_URL}/blog/synbiotics-absorption.html", "category": "Wellness"},
    {"title": "Agar Work: Isolating Clean Genetics at Home", "url": f"{SITE_URL}/blog/agar-work-isolating-genetics.html", "category": "Cultivation"},
    {"title": "Cordyceps vs Pre-Workout: Natural ATP Enhancement", "url": f"{SITE_URL}/blog/cordyceps-vs-pre-workout.html", "category": "Wellness"},
    {"title": "ViaCap Microencapsulation & Gut Transit Technology", "url": f"{SITE_URL}/blog/viacap-microencapsulation-gut-transit.html", "category": "Wellness"},
]

INTERACTIVE_TOOLS = [
    {"title": "Mycology Finder Quiz", "url": f"{SITE_URL}/tools/mycology-finder.html", "desc": "Answer 3 quick questions and get matched with the perfect mushroom product for your goals."},
    {"title": "Yield Estimator Calculator", "url": f"{SITE_URL}/tools/yield-estimator.html", "desc": "Calculate expected mushroom yields based on species, substrate type, and container size."},
    {"title": "Substrate Calculator (CVG)", "url": f"{SITE_URL}/tools/substrate-calculator.html", "desc": "Get exact coir, vermiculite, gypsum, and water ratios for any tub size."},
    {"title": "Wellness Stack Builder", "url": f"{SITE_URL}/tools/wellness-stack-builder.html", "desc": "Build a personalized daily supplement stack based on your health goals."},
    {"title": "Contamination Diagnostics Guide", "url": f"{SITE_URL}/tools/diagnostics.html", "desc": "Identify and diagnose common mushroom grow contamination issues with visual symptom matching."},
]

MYCOLOGY_DIRECTORIES = [
    {"name": "Mycological Society of America", "url": "https://msafungi.org/", "type": "Professional society", "action": "Submit as educational resource link"},
    {"name": "Shroomery.org", "url": "https://www.shroomery.org/", "type": "Community forum", "action": "Create profile, contribute to relevant threads"},
    {"name": "r/mycology", "url": "https://reddit.com/r/mycology", "type": "Reddit community", "action": "Share research articles and tools naturally"},
    {"name": "r/MushroomGrowers", "url": "https://reddit.com/r/MushroomGrowers", "type": "Reddit community", "action": "Share cultivation guides and yield calculator"},
    {"name": "r/unclebens", "url": "https://reddit.com/r/unclebens", "type": "Reddit community", "action": "Share contamination diagnostics and monotub guide"},
    {"name": "r/Supplements", "url": "https://reddit.com/r/Supplements", "type": "Reddit community", "action": "Share Lion's Mane and Cordyceps research articles"},
    {"name": "r/Nootropics", "url": "https://reddit.com/r/Nootropics", "type": "Reddit community", "action": "Share Lion's Mane neurogenesis research"},
    {"name": "NAMA (North American Mycological Assoc.)", "url": "https://namyco.org/", "type": "Professional society", "action": "Submit for resources/links page"},
    {"name": "Fungi Perfecti Community", "url": "https://fungi.com/", "type": "Industry leader", "action": "Engage with community content"},
    {"name": "Pinterest — Mushroom Cultivation", "url": "https://pinterest.com/", "type": "Visual platform", "action": "Pin tool screenshots and infographics with backlinks"},
]

GUEST_POST_TARGETS = [
    {"blog": "GroCycle.com", "topic": "Beginner's guide to home mushroom cultivation", "angle": "Include link to SporlyWorks Yield Estimator as a resource"},
    {"blog": "FungiFact.com", "topic": "The science behind functional mushroom supplements", "angle": "Reference SporlyWorks beta-glucan extraction methods article"},
    {"blog": "MycoRising.com", "topic": "Liquid culture vs spore syringes for inoculation", "angle": "Link to SporlyWorks comparison guide and Mycology Finder quiz"},
    {"blog": "FreshCap.com/blog", "topic": "How Lion's Mane supports brain health", "angle": "Cross-reference SporlyWorks neurogenesis research article"},
    {"blog": "NorthSpore.com/blog", "topic": "Troubleshooting contamination in your grow", "angle": "Link to SporlyWorks diagnostics tool and contamination guide"},
    {"blog": "TheMushroomForager.com", "topic": "From foraging to cultivation: growing your own at home", "angle": "Reference SporlyWorks substrate calculator and grow kit reviews"},
    {"blog": "Healthline.com", "topic": "Evidence-based benefits of adaptogenic mushrooms", "angle": "Pitch as expert contributor, reference SporlyWorks research blog"},
    {"blog": "MindBodyGreen.com", "topic": "Natural nootropics for cognitive performance", "angle": "Pitch as contributor, reference Lion's Mane and Cordyceps articles"},
]


def get_week_number():
    """Get ISO week number for content rotation."""
    return datetime.date.today().isocalendar()[1]


def generate_reddit_drafts():
    """Generate weekly Reddit post drafts that naturally include backlinks."""
    week = get_week_number()
    drafts = []

    # Select 2 articles and 1 tool per week, rotating based on week number
    article_pool = BLOG_ARTICLES.copy()
    random.seed(week)
    random.shuffle(article_pool)
    selected_articles = article_pool[:2]
    selected_tool = INTERACTIVE_TOOLS[week % len(INTERACTIVE_TOOLS)]

    for article in selected_articles:
        if article["category"] == "Cultivation":
            subreddit = random.choice(["r/MushroomGrowers", "r/mycology", "r/unclebens"])
        elif article["category"] == "Wellness":
            subreddit = random.choice(["r/Supplements", "r/Nootropics", "r/mycology"])
        else:
            subreddit = "r/mycology"

        draft = {
            "platform": f"Reddit — {subreddit}",
            "title": article["title"],
            "body": f"I put together a detailed write-up on this topic with references to peer-reviewed studies. "
                    f"Covers the science, practical applications, and common misconceptions.\n\n"
                    f"Full article: {article['url']}\n\n"
                    f"Happy to answer any questions or discuss further in the comments.",
            "url": article["url"],
            "note": "POST MANUALLY — Do not automate Reddit posting. Engage authentically in comments."
        }
        drafts.append(draft)

    # Tool post
    tool_draft = {
        "platform": f"Reddit — r/MushroomGrowers",
        "title": f"Free Tool: {selected_tool['title']}",
        "body": f"Built a free {selected_tool['title'].lower()} for the community. {selected_tool['desc']}\n\n"
                f"No signup required, completely free: {selected_tool['url']}\n\n"
                f"Let me know if there are features you'd want added!",
        "url": selected_tool["url"],
        "note": "POST MANUALLY — Share tools as community value-adds, not promotions."
    }
    drafts.append(tool_draft)

    return drafts


def generate_pinterest_drafts():
    """Generate Pinterest pin descriptions with backlinks."""
    week = get_week_number()
    pins = []

    random.seed(week + 100)
    articles = BLOG_ARTICLES.copy()
    random.shuffle(articles)

    for article in articles[:3]:
        pin = {
            "board": f"Mushroom {article['category']}" if article["category"] != "Microscopy" else "Mycology Research",
            "title": article["title"],
            "description": f"{article['title']} — In-depth guide with peer-reviewed references. "
                          f"Read the full article at {article['url']} | "
                          f"#functionalmushrooms #mycology #mushroomcultivation #adaptogens #sporlyworks",
            "url": article["url"]
        }
        pins.append(pin)

    # Pin for interactive tool
    tool = INTERACTIVE_TOOLS[week % len(INTERACTIVE_TOOLS)]
    pins.append({
        "board": "Mycology Tools",
        "title": f"Free {tool['title']}",
        "description": f"{tool['desc']} Try it free at {tool['url']} | "
                      f"#mushroomgrowing #mycologytools #shroomtek #sporlyworks",
        "url": tool["url"]
    })

    return pins


def generate_guest_post_pitches():
    """Generate guest post pitch emails for mycology blogs."""
    week = get_week_number()
    random.seed(week + 200)
    targets = GUEST_POST_TARGETS.copy()
    random.shuffle(targets)
    selected = targets[:2]

    pitches = []
    for target in selected:
        pitch = {
            "target_blog": target["blog"],
            "subject": f"Guest Post Pitch: {target['topic']}",
            "body": (
                f"Hi there,\n\n"
                f"I'm reaching out from SporlyWorks — we publish peer-reviewed mycology research "
                f"and free interactive tools for the home cultivation and functional mushroom community.\n\n"
                f"I'd love to contribute a guest article on \"{target['topic']}\" for your readers. "
                f"{target['angle']}.\n\n"
                f"We have a growing library of research-backed content at {SITE_URL}/blog/index.html "
                f"and free tools like our Yield Estimator ({SITE_URL}/tools/yield-estimator.html) "
                f"that your audience might find valuable.\n\n"
                f"Would you be open to a guest contribution? Happy to tailor the piece to your editorial style.\n\n"
                f"Best,\nSporlyWorks Team\n{SITE_URL}"
            ),
            "note": "SEND MANUALLY — Personalize before sending. Research the blog's recent content first."
        }
        pitches.append(pitch)

    return pitches


def generate_directory_submissions():
    """Generate structured data for web directory submissions."""
    return {
        "site_name": SITE_NAME,
        "url": SITE_URL,
        "category": "Science > Biology > Mycology",
        "alt_categories": [
            "Health > Supplements > Mushroom Extracts",
            "Shopping > Health > Natural Products",
            "Science > Biology > Fungi"
        ],
        "description_short": SITE_DESCRIPTION,
        "description_long": (
            "SporlyWorks is a research-driven mycology and wellness platform offering certified spore genetics "
            "for microscopy study, organic grow kits for home mushroom cultivation, and clinically-studied "
            "adaptogenic mushroom supplements. Features include free interactive tools (Yield Estimator, "
            "Substrate Calculator, Mycology Finder Quiz), peer-reviewed research articles, and partnerships "
            "with premium suppliers including MYYCO, North Spore, Magic Bag, and Real Mushrooms."
        ),
        "target_directories": MYCOLOGY_DIRECTORIES,
        "keywords": [
            "mushroom cultivation", "spore syringe", "liquid culture", "mycology",
            "lions mane supplement", "cordyceps extract", "reishi mushroom",
            "mushroom grow kit", "substrate calculator", "functional mushrooms",
            "adaptogenic supplements", "microscopy research", "beta-glucan"
        ]
    }


def generate_weekly_report():
    """Generate the weekly backlink opportunity report."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    week = get_week_number()

    reddit_drafts = generate_reddit_drafts()
    pinterest_pins = generate_pinterest_drafts()
    guest_pitches = generate_guest_post_pitches()
    directory_data = generate_directory_submissions()

    report = f"# SporlyWorks Weekly Link Building Report\n"
    report += f"_Week {week} — Generated {today}_\n\n"
    report += "---\n\n"

    # Reddit Drafts
    report += "## 📝 Reddit Post Drafts (Post Manually)\n\n"
    for draft in reddit_drafts:
        report += f"### {draft['platform']}\n"
        report += f"**Title:** {draft['title']}\n\n"
        report += f"**Body:**\n> {draft['body'].replace(chr(10), chr(10) + '> ')}\n\n"
        report += f"**Link:** {draft['url']}\n\n"
        report += f"⚠️ _{draft['note']}_\n\n---\n\n"

    # Pinterest Pins
    report += "## 📌 Pinterest Pin Drafts\n\n"
    for pin in pinterest_pins:
        report += f"### Board: {pin['board']}\n"
        report += f"**Title:** {pin['title']}\n\n"
        report += f"**Description:** {pin['description']}\n\n"
        report += f"**Link:** {pin['url']}\n\n---\n\n"

    # Guest Post Pitches
    report += "## ✉️ Guest Post Pitch Drafts (Send Manually)\n\n"
    for pitch in guest_pitches:
        report += f"### Target: {pitch['target_blog']}\n"
        report += f"**Subject:** {pitch['subject']}\n\n"
        report += f"**Email Body:**\n```\n{pitch['body']}\n```\n\n"
        report += f"⚠️ _{pitch['note']}_\n\n---\n\n"

    # Directory Submissions
    report += "## 🌐 Directory Submission Targets\n\n"
    report += f"**Site:** {directory_data['site_name']} — {directory_data['url']}\n\n"
    report += f"**Category:** {directory_data['category']}\n\n"
    report += "| Directory | Type | Action |\n|---|---|---|\n"
    for d in directory_data["target_directories"]:
        report += f"| [{d['name']}]({d['url']}) | {d['type']} | {d['action']} |\n"
    report += "\n"

    # Save report
    report_path = os.path.join(OUTPUT_DIR, f"weekly_report_w{week}.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"✅ Weekly link building report generated: {report_path}")

    # Save structured JSON for programmatic use
    json_data = {
        "week": week,
        "date": today,
        "reddit_drafts": reddit_drafts,
        "pinterest_pins": pinterest_pins,
        "guest_pitches": guest_pitches,
        "directory_data": directory_data
    }
    json_path = os.path.join(OUTPUT_DIR, f"weekly_data_w{week}.json")
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"✅ Structured data saved: {json_path}")

    return report_path


if __name__ == "__main__":
    print("=" * 60)
    print("  🔗 SporlyWorks Automated Link Building Engine")
    print("=" * 60)
    report_path = generate_weekly_report()
    print(f"\n📄 Full report: {report_path}")
    print("=" * 60)
