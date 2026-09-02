#!/usr/bin/env python3
import os
import json
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOCIAL_DIR = os.path.join(BASE_DIR, "_social_engine")
QUEUE_DIR = os.path.join(SOCIAL_DIR, "_queue")
os.makedirs(QUEUE_DIR, exist_ok=True)

# Post templates following non-AI human style guidelines
POST_TEMPLATES = [
    {
        "id": 1,
        "pillar": "Science",
        "title": "Why Hericenones need healthy fats",
        "caption": (
            "We talk a lot about Lion's Mane and cognitive clarity, but the chemistry of absorption matters. "
            "The active compounds responsible for stimulating Nerve Growth Factor (NGF)—hericenones and erinacines—are lipophilic. "
            "This means they are fat-soluble. If you take your supplement powder in plain water on an empty stomach, your absorption rate is significantly degraded. "
            "To get the most out of your dose, stack it with a healthy fat source. Mix your powder into bulletproof coffee, pair it with an avocado, or take it alongside your Omega-3 softgels. "
            "Read our complete scientific analysis on Hericium erinaceus absorption kinetics: sporlyworks.com/blog/lions-mane-neurogenesis.html\n\n"
            "#mycology #neurogenesis #lionsmane #functionalmushrooms #stackbuilding #biohacking"
        ),
        "visual_prompt": "Clean, minimalist diagram showing Lion's Mane active compounds (Hericenones) binding to lipids (fats) for cellular transport. Solid cream background with forest green ink line-art."
    },
    {
        "id": 2,
        "pillar": "Cultivation",
        "title": "Trichoderma vs Bruising: The H2O2 test",
        "caption": (
            "The single most common panic for new cultivators is seeing their mycelium turn blue-gray. "
            "Here is how to tell the difference between bruising and green mold (Trichoderma):\n\n"
            "1. Bruising is chemical. Cell walls oxidize from rough misting or dry air. It is dull blue and stays localized.\n"
            "2. Trichoderma is parasitic. It starts as a powdery bright white patch, then shifts to forest green as it releases spores. It grows aggressively.\n\n"
            "If you are unsure, do the Peroxide test: apply a drop of 3% H2O2. If it is Cobweb mold, it will instantly fizzle and melt. If it is healthy mycelium, it will remain intact. "
            "Never open a green bag in your cleanroom. "
            "Use our free interactive Grow Diagnostics Tool to diagnose your substrate: sporlyworks.com/tools/diagnostics.html\n\n"
            "#mushroomcultivation #homegrower #mycology #trichoderma #steriletechnique #sporelyworks"
        ),
        "visual_prompt": "Before and after visual flowchart showing how to perform the 3% H2O2 test on suspicious substrate growth. Cream and forest-green vector sketch."
    },
    {
        "id": 3,
        "pillar": "Gut Health",
        "title": "The gastric acid barrier in probiotics",
        "caption": (
            "Stomach acid sits at a pH of 1.5 to 3.5. This is highly acidic, designed to destroy pathogens. "
            "It also destroys up to 90% of standard probiotic capsules before they ever reach your lower intestine. "
            "This is why Colony Forming Unit (CFU) counts on supplement labels are often misleading. A 50 Billion CFU count doesn't matter if 49 Billion cells are denatured in gastric acid. "
            "To bypass this, look for a dual-capsule delivery system (like Seed's DS-01). The outer capsule acts as a prebiotic buffer, shielding the inner probiotic capsule until it reaches the small intestine. "
            "Read our breakdown of probiotic gastric survivability kinetics: sporlyworks.com/blog/synbiotics-absorption.html\n\n"
            "#guthealth #microbiome #probiotics #synbiotics #seedprobiotics #bioavailability"
        ),
        "visual_prompt": "Minimalist cross-section diagram of a dual-capsule probiotic system surviving stomach acid. Solid cream background, forest-green borders."
    }
]

def initialize_queue():
    for post in POST_TEMPLATES:
        filename = f"post_{post['id']}_{post['pillar'].lower()}.json"
        filepath = os.path.join(QUEUE_DIR, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(post, f, indent=2)
            print(f"Queued Post {post['id']}: {filepath}")

def show_menu():
    print("==================================================")
    print("      SPORLYWORKS SOCIAL SCHEDULER DAEMON        ")
    print("==================================================")
    print("1. View Active Queue / Draft Posts")
    print("2. Prepare Post for @sporlyworks (Copy Caption)")
    print("3. Add New Custom Draft")
    print("4. Exit")
    print("==================================================")

def run():
    initialize_queue()
    while True:
        show_menu()
        choice = input("Select an option (1-4): ").strip()
        if choice == "1":
            print("\nActive Queue:")
            files = sorted([f for f in os.listdir(QUEUE_DIR) if f.endswith(".json")])
            if not files:
                print("Queue is empty.")
            for f in files:
                with open(os.path.join(QUEUE_DIR, f), 'r') as file:
                    data = json.load(file)
                    print(f"[{art_status(data)}] ID {data['id']} | Pillar: {data['pillar']} | Title: {data['title']}")
            print()
        elif choice == "2":
            post_id = input("Enter Post ID to prepare: ").strip()
            files = [f for f in os.listdir(QUEUE_DIR) if f.endswith(".json")]
            found = False
            for f in files:
                with open(os.path.join(QUEUE_DIR, f), 'r') as file:
                    data = json.load(file)
                    if str(data['id']) == post_id:
                        found = True
                        print(f"\n--- CAPTION FOR @sporlyworks ---")
                        print(data['caption'])
                        print("--------------------------------")
                        print(f"VISUAL PROMPT FOR POST IMAGE:")
                        print(f"-> {data['visual_prompt']}\n")
                        # Try to copy to clipboard using pbcopy on macOS
                        try:
                            os.system(f"echo '{data['caption']}' | pbcopy")
                            print("✅ Caption copied to clipboard (macOS clipboard integration)!")
                        except:
                            pass
                        break
            if not found:
                print("Post ID not found.")
            print()
        elif choice == "3":
            print("\nCreate a New Custom Draft:")
            title = input("Enter Title: ").strip()
            pillar = input("Enter Pillar (e.g. Science, Cultivation): ").strip()
            caption = input("Enter Caption: ").strip()
            prompt = input("Enter Visual Prompt/Description: ").strip()
            
            # Find next ID
            files = [f for f in os.listdir(QUEUE_DIR) if f.endswith(".json")]
            max_id = 0
            for f in files:
                with open(os.path.join(QUEUE_DIR, f), 'r') as file:
                    data = json.load(file)
                    max_id = max(max_id, data['id'])
            
            new_post = {
                "id": max_id + 1,
                "pillar": pillar,
                "title": title,
                "caption": caption,
                "visual_prompt": prompt
            }
            
            filename = f"post_{new_post['id']}_{pillar.lower()}.json"
            with open(os.path.join(QUEUE_DIR, filename), 'w') as file:
                json.dump(new_post, file, indent=2)
            print(f"✅ Post draft created successfully at {filename}!\n")
        elif choice == "4":
            print("Exiting scheduler. Be well.")
            break
        else:
            print("Invalid selection. Try again.\n")

def art_status(data):
    # Status helper
    return "READY"

if __name__ == "__main__":
    run()
