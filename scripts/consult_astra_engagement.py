#!/usr/bin/env python3
"""
Consult Astra (OpenAI Astra / GPT-4o) for SporlyWorks Instagram Follow & Engagement Growth Engine.
Single targeted query with minimal token usage.
"""

import os
import sys
import json
import urllib.request
import urllib.error

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODELS = ["gpt-4o", "gpt-4-turbo"]

PROMPT = """
You are Astra, Principal Social Growth Architect & Automation Engineer for SporlyWorks (https://sporlyworks.com).

MISSION:
Design an automated Instagram organic growth system for @SporlyWorks to auto-follow and auto-comment on the right profiles at an authentic, human rate to grow the channel as rapidly and safely as possible without triggering Instagram action blocks or shadowbans.

REQUIREMENTS:
1. Target Profile Archetypes:
   - Identify the exact targets: micro-cultivators (1k-15k followers), niche hashtags, and followers of established peer brands (e.g. North Spore, Myyco, FreshCap, Magic Bag, Mushroom Revival).
   - Filter criteria: accounts that actively post cultivation/mycology content, high follow-back probability, genuine interest in calculators/substrates/genetics.
2. Safe Human Pacing & Rate Limits:
   - Specific hourly and daily maximums for:
     a) Follows per hour / day
     b) Comments per hour / day
     c) Likes per hour / day
   - Randomized delay windows (seconds) between actions to mimic human browsing.
3. High-Converting, Anti-Bot Comment Strategy:
   - Provide 5 distinct comment archetypes that NEVER pitch a link or say "nice post", but instead add peer expertise, ask a provocative technical question about their agar/substrate/flush, or validate their technique so the creator & comment readers click through to @SporlyWorks.
4. State Tracking & Unfollow Hygiene:
   - How to manage the follow ledger (database/json) to avoid re-following, and safely prune non-reciprocating accounts after 7-10 days to keep the follower/following ratio healthy.
5. System Architecture:
   - Clear step-by-step logic for the Python execution engine.

Provide a concise, highly tactical blueprint in Markdown.
"""

def consult_astra():
    if not OPENAI_API_KEY:
        print("[!] ERROR: OPENAI_API_KEY is not set.")
        sys.exit(1)

    response_text = None
    for model in MODELS:
        print(f"[*] Consulting Astra via model: {model}...")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are Astra, Principal Growth Architect. Give concise, actionable, high-impact growth automation blueprints."},
                {"role": "user", "content": PROMPT}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
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
                print(f"✅ Successfully received engagement plan from {model}!")
                break
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"⚠️ Model {model} failed (HTTP {e.code}): {err_body[:120]}...")
        except Exception as ex:
            print(f"⚠️ Model {model} error: {ex}...")

    if not response_text:
        print("[-] Could not retrieve plan from Astra.")
        sys.exit(1)

    out_file = os.path.join(os.path.dirname(__file__), "..", "scratch", "astra_instagram_engagement_plan.md")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(response_text)

    print(f"📁 Plan written to: {out_file}")
    return response_text

if __name__ == "__main__":
    consult_astra()
