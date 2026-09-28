#!/usr/bin/env python3
"""
Consult Astra (GPT-6 Astra) for SporlyWorks Instagram Strategy
Queries Astra with minimal token usage to formulate a high-converting,
non-AI-sounding, viral Instagram content and visual execution plan.
"""

import os
import sys
import json
import urllib.request
import urllib.error

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODELS = ["gpt-6-astra", "gpt-4o", "gpt-4-turbo"]

PROMPT = """
You are Astra, Principal Growth Strategist and Viral Social Architect for SporlyWorks (https://sporlyworks.com).

SporlyWorks is a precision mycology & cognitive health platform featuring interactive tools (Substrate Hydration Calculator, Biological Efficiency Estimator, Inoculation & Grain Spawn Ratios), functional mushroom extract guides (Lion's Mane, Cordyceps, Reishi), and clean cultivation protocols.

USER DIRECTIVE:
The previous automated Instagram post was too generic and felt like a sterile textbook summary.
We need an immediate, upgraded strategy and exact post template that:
1. Maximizes authentic engagement, saves, and shares across mycology cultivators, growers, and biohackers.
2. Completely avoids sounding generic, corporate, or AI-generated. It should read like an experienced field cultivator / sterile-lab technician sharing hard-won benchmarks, counter-intuitive field truths, and zero-fluff parameters.
3. Strategically promotes sporlyworks.com and drives organic visits to our interactive calculators without being an obnoxious sales pitch.
4. Outlines the visual aesthetic: high-contrast, beautiful parchment/earth tones, featuring our official website emblem logo (assets/logo-nav.png), clean typography, and screenshot-worthy parameter cards / cheat sheets.

DELIVERABLES NEEDED IN DETAIL:
1. The Core Engagement Framework (Hooks, tone, formatting rules, comment baiting, and shareability triggers).
2. The Visual Graphic Blueprint (Exact layout of the 1080x1080 image to make it look like a premium lab protocol card that gets saved to collections).
3. 3 High-Impact Master Posts (Complete with Title, Graphic Hook Text, Sub-Parameters, Scientific Source, Captivating Body Copy, and Natural Call-to-Action for sporlyworks.com tools):
   - Post A: Cultivation / Substrate Mastery (e.g. Field Capacity Truth & Contamination Prevention)
   - Post B: Functional Extraction / Nootropic Science (e.g. Hot Water vs Alcohol: The Dual-Extract Trap)
   - Post C: Biology & Genetics (e.g. Liquid Culture vs Agar: Isolating Rhizomorphic Growth)

Format in crisp, actionable Markdown.
"""

def query_astra():
    if not OPENAI_API_KEY:
        print("[!] ERROR: OPENAI_API_KEY is not set.")
        sys.exit(1)

    response_text = None
    for model in MODELS:
        print(f"[*] Consulting Astra via model: {model}...")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are Astra, Principal Growth Architect. Provide concise, high-converting, execution-ready directives."},
                {"role": "user", "content": PROMPT}
            ],
            "temperature": 0.7,
            "max_tokens": 2500
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                response_text = res_data["choices"][0]["message"]["content"]
                print(f"✅ Successfully received plan from {model}!")
                break
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"⚠️ Model {model} failed (HTTP {e.code}): {err_body[:120]}... Trying next model.")
        except Exception as ex:
            print(f"⚠️ Model {model} error: {ex}... Trying next model.")

    if not response_text:
        print("[-] Could not retrieve plan from any OpenAI model.")
        sys.exit(1)

    out_file = os.path.join(os.path.dirname(__file__), "..", "scratch", "astra_instagram_viral_plan.md")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(response_text)

    print(f"📁 Plan written to: {out_file}")
    return response_text

if __name__ == "__main__":
    query_astra()
