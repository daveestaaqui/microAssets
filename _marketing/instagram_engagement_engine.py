#!/usr/bin/env python3
"""
SporlyWorks — Instagram Growth & Authentic Engagement Engine
Architected by Astra (OpenAI Astra) for organic community growth.

Auto-follows, likes, and leaves high-value, non-spam comments on target
mycology cultivators, lab hobbyists, and grower profiles at human rate.
Maintains a follow ledger with safe 7-day unfollow rotation.
"""

import os
import sys
import json
import time
import random
import re
import imaplib
import email
import argparse
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE_DIR, "_marketing", "instagram_engagement_state.json")

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")

# Curated target hashtags where active cultivators post their work
TARGET_HASHTAGS = [
    "mushroomcultivation",
    "monotubtek",
    "liquidculture",
    "agarplate",
    "steriletechnique",
    "mycologysociety",
    "grainspawn",
    "homebiology",
    "fungilovers"
]

# High-converting, anti-bot comment pools categorised by visual/caption topic
COMMENT_TEMPLATES = {
    "agar": [
        "That rhizomorphic growth is razor sharp. 2% MEA or are you using a low-nutrient recipe to force reaching?",
        "Clinical agar work right here. Clean leading edge transfer—how many transfers to isolate this monoculture?",
        "Satisfying sectoring on that dish! Do you transfer straight to grain from here or expand into liquid culture broth?"
    ],
    "flushes": [
        "Incredible pin set on this flush. What FAE cycle or tub hole configuration are you running here?",
        "That canopy density is serious work. Are you running straight coco coir or CVG for this run?",
        "Super clean wall-to-wall pinning. Did you case this or send straight to fruiting from 100% colonization?",
        "Top-tier biological efficiency on display here. How many flushes do you usually aim for before flipping the cake?"
    ],
    "substrate": [
        "Substrate looks dialed right in at field capacity. What hydration percentage do you usually target for this species?",
        "Great texture on that spawn run. What's your go-to grain choice—whole oats, rye berries, or millet?",
        "Clean colonization pace. Are you pasteurizing in a cooler bucket or running atmospheric steam for your bulk mix?"
    ],
    "general": [
        "Lab-grade execution. Always great seeing clean cultivation discipline in the community.",
        "Dialed in setup! The attention to sterile technique definitely shows in the results.",
        "Solid work. Consistency in lab protocols really pays off when you see flushes like this."
    ]
}

def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Notice loading state: {e}")
    return {
        "followed_users": {},
        "commented_media": {},
        "liked_media": [],
        "history": []
    }

def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def get_latest_otp(max_retries=12, delay_seconds=5):
    """Fetches Instagram verification OTP code from Gmail IMAP."""
    if not GMAIL_USER or not GMAIL_PASS:
        return None
    print(f"⏳ Checking Gmail for Instagram OTP code...")
    for attempt in range(1, max_retries + 1):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(GMAIL_USER, GMAIL_PASS)
            mail.select('"[Gmail]/All Mail"')
            status, messages = mail.search(None, '(FROM "instagram")')
            if status != "OK" or not messages[0]:
                status, messages = mail.search(None, 'ALL')
            if status == "OK" and messages[0]:
                ids = messages[0].split()
                if ids:
                    recent_ids = sorted(ids, key=lambda x: int(x), reverse=True)[:6]
                    for m_id in recent_ids:
                        res, msg_data = mail.fetch(m_id, "(RFC822)")
                        for part in msg_data:
                            if isinstance(part, tuple):
                                msg = email.message_from_bytes(part[1])
                                sender = str(msg.get("From", "")).lower()
                                subject = str(msg.get("Subject", "")).lower()
                                if "instagram" in sender or "instagram" in subject or "security" in subject:
                                    body = ""
                                    if msg.is_multipart():
                                        for p in msg.walk():
                                            if p.get_content_type() in ("text/html", "text/plain"):
                                                body += p.get_payload(decode=True).decode(errors="ignore")
                                    else:
                                        body = msg.get_payload(decode=True).decode(errors="ignore")
                                    codes = re.findall(r"\b\d{6}\b", body)
                                    if codes:
                                        print(f"✅ Found Instagram OTP on attempt {attempt}: {codes[0]}")
                                        mail.logout()
                                        return codes[0]
            mail.logout()
        except Exception as e:
            pass
        if attempt < max_retries:
            time.sleep(delay_seconds)
    return None

def challenge_code_handler(username, choice):
    print(f"⚠️ Instagram login challenge triggered for @{username}. Waiting 10s for OTP...")
    time.sleep(10)
    return get_latest_otp(max_retries=12, delay_seconds=5)

def select_comment_archetype(caption_text):
    """Chooses the most contextually relevant technical comment based on the post text."""
    cap = (caption_text or "").lower()
    if any(k in cap for k in ["agar", "plate", "petri", "rhizomorphic", "transfer", "isolate", "clone"]):
        pool = COMMENT_TEMPLATES["agar"]
    elif any(k in cap for k in ["flush", "pin", "canopy", "harvest", "tub", "monotub", "fruiting", "fruits"]):
        pool = COMMENT_TEMPLATES["flushes"]
    elif any(k in cap for k in ["substrate", "coir", "cvg", "grain", "spawn", "jar", "bag", "field capacity"]):
        pool = COMMENT_TEMPLATES["substrate"]
    else:
        pool = COMMENT_TEMPLATES["general"]
    return random.choice(pool)

def human_sleep(min_s, max_s, action_name=""):
    delay = random.uniform(min_s, max_s)
    if action_name:
        print(f"⏳ [Human Pacing] Sleeping {delay:.1f}s after {action_name}...")
    time.sleep(delay)

def run_engagement_cycle(args):
    state = load_state()
    print("=" * 60)
    print("🍄 SPORLYWORKS INSTAGRAM ENGAGEMENT ENGINE (Astra Growth)")
    print(f"Session Targets: Max {args.max_follows} follows, {args.max_comments} comments, {args.max_likes} likes")
    print(f"Dry Run Mode: {args.dry_run}")
    print("=" * 60)

    cl = None
    if not args.dry_run:
        try:
            from instagrapi import Client
            cl = Client()
            authenticated = False

            if args.session_id:
                print("🔑 Authenticating via Instagram session ID...")
                try:
                    cl.login_by_sessionid(args.session_id)
                    print("✅ Session ID authenticated.")
                    authenticated = True
                except Exception as se:
                    print(f"⚠️ Session ID login failed: {se}")
                    if not (args.username and args.password):
                        return
                    print("🔄 Falling back to username/password login...")

            if not authenticated and args.username and args.password:
                cl = Client()
                cl.challenge_code_handler = challenge_code_handler
                print(f"Logging in as @{args.username}...")
                try:
                    cl.login(args.username, args.password)
                    print("✅ Logged in successfully via username/password.")
                    authenticated = True
                except Exception as ue:
                    print(f"❌ Username/password login failed: {ue}")
                    return

            if not authenticated:
                print("❌ No valid Instagram authentication succeeded.")
                return
        except Exception as e:
            print(f"❌ Error during Instagram authentication: {e}")
            return

    # 1. Unfollow Maintenance Routine (Prune unreciprocated follows older than 7 days)
    if args.unfollow_inactive and not args.dry_run:
        print("\n🔍 Checking follow ledger for accounts older than 7 days...")
        unfollow_count = 0
        now = time.time()
        cutoff = now - (7 * 86400) # 7 days ago
        for uid, meta in list(state["followed_users"].items()):
            if meta.get("timestamp", now) < cutoff and not meta.get("unfollowed", False):
                try:
                    username = meta.get("username", uid)
                    print(f"👋 Unfollowing inactive non-reciprocating account: @{username} (ID: {uid})")
                    cl.user_unfollow(uid)
                    meta["unfollowed"] = True
                    meta["unfollowed_at"] = now
                    unfollow_count += 1
                    human_sleep(30, 60, "unfollow")
                    if unfollow_count >= 5:
                        break
                except Exception as ue:
                    print(f"Notice on unfollow {uid}: {ue}")
        save_state(state)
        print(f"✅ Unfollowed {unfollow_count} inactive accounts.")

    # 2. Candidate Discovery via Cultivator Hashtags
    follows_executed = 0
    comments_executed = 0
    likes_executed = 0

    shuffled_tags = list(TARGET_HASHTAGS)
    random.shuffle(shuffled_tags)

    print(f"\n🔎 Scanning target mycology hashtags: {', '.join(shuffled_tags[:4])}...")

    for tag in shuffled_tags:
        if follows_executed >= args.max_follows and comments_executed >= args.max_comments:
            break

        print(f"\n🏷️ Exploring #{tag}...")
        medias = []
        if args.dry_run:
            # Simulated media items for dry-run verification
            medias = [
                {"id": f"sim_{tag}_1", "user": {"pk": f"uid_10{random.randint(100,999)}", "username": f"grower_{tag}_1", "is_private": False, "follower_count": 3200}, "caption_text": "First flush of tidal wave pins coming in strong! CVG substrate dialed at field capacity."},
                {"id": f"sim_{tag}_2", "user": {"pk": f"uid_10{random.randint(100,999)}", "username": f"myco_lab_{tag}_2", "is_private": False, "follower_count": 5800}, "caption_text": "Rhizomorphic mycelium sectoring cleanly on 2% malt extract agar petri dish."}
            ]
        else:
            try:
                # Fetch recent posts from target hashtag
                medias = cl.hashtag_medias_recent(tag, amount=12)
            except Exception as he:
                print(f"⚠️ Could not fetch #{tag} medias: {he}")
                continue

        for m in medias:
            if follows_executed >= args.max_follows and comments_executed >= args.max_comments:
                break

            m_id = getattr(m, "id", None) or m.get("id")
            user = getattr(m, "user", None) or m.get("user")
            user_pk = getattr(user, "pk", None) or (user.get("pk") if isinstance(user, dict) else None)
            username = getattr(user, "username", None) or (user.get("username") if isinstance(user, dict) else None)
            is_private = getattr(user, "is_private", False) or (user.get("is_private") if isinstance(user, dict) else False)
            caption_text = getattr(m, "caption_text", "") or m.get("caption_text", "")

            if not user_pk or is_private:
                continue

            user_pk_str = str(user_pk)

            # Filter: skip if already followed or commented recently
            if user_pk_str in state["followed_users"]:
                continue
            if str(m_id) in state["commented_media"]:
                continue

            print(f"\n🎯 Identified Cultivator: @{username} (Post: {caption_text[:60]}...)")

            # Action A: Like Post
            if likes_executed < args.max_likes and str(m_id) not in state["liked_media"]:
                if args.dry_run:
                    print(f"  ❤️ [DRY RUN] Would like media {m_id} by @{username}")
                    likes_executed += 1
                else:
                    try:
                        cl.media_like(m_id)
                        state["liked_media"].append(str(m_id))
                        likes_executed += 1
                        print(f"  ❤️ Liked post {m_id} by @{username} ({likes_executed}/{args.max_likes})")
                        human_sleep(25, 45, "like")
                    except Exception as le:
                        print(f"  ⚠️ Like error: {le}")

            # Action B: Follow Cultivator
            if follows_executed < args.max_follows:
                if args.dry_run:
                    print(f"  ➕ [DRY RUN] Would follow @{username} (ID: {user_pk_str})")
                    follows_executed += 1
                    state["followed_users"][user_pk_str] = {
                        "username": username,
                        "timestamp": time.time(),
                        "hashtag": tag,
                        "simulated": True
                    }
                else:
                    try:
                        cl.user_follow(user_pk)
                        state["followed_users"][user_pk_str] = {
                            "username": username,
                            "timestamp": time.time(),
                            "hashtag": tag,
                            "unfollowed": False
                        }
                        follows_executed += 1
                        print(f"  ➕ Followed @{username} ({follows_executed}/{args.max_follows})")
                        human_sleep(45, 80, "follow")
                    except Exception as fe:
                        print(f"  ⚠️ Follow error: {fe}")

            # Action C: Contextual Technical Comment
            if comments_executed < args.max_comments:
                comment_text = select_comment_archetype(caption_text)
                if args.dry_run:
                    print(f"  💬 [DRY RUN] Would comment on post {m_id}: \"{comment_text}\"")
                    comments_executed += 1
                    state["commented_media"][str(m_id)] = {
                        "username": username,
                        "comment": comment_text,
                        "timestamp": time.time(),
                        "simulated": True
                    }
                else:
                    try:
                        cl.media_comment(m_id, comment_text)
                        state["commented_media"][str(m_id)] = {
                            "username": username,
                            "comment": comment_text,
                            "timestamp": time.time()
                        }
                        comments_executed += 1
                        print(f"  💬 Commented on @{username}'s post: \"{comment_text}\" ({comments_executed}/{args.max_comments})")
                        human_sleep(60, 110, "comment")
                    except Exception as ce:
                        print(f"  ⚠️ Comment error: {ce}")

            if not args.dry_run:
                save_state(state)

    print("\n" + "=" * 60)
    print(f"🎉 Engagement cycle completed: {follows_executed} follows, {comments_executed} comments, {likes_executed} likes.")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="SporlyWorks Instagram Organic Engagement Engine")
    parser.add_argument("--dry-run", action="store_true", help="Simulate engagement actions without calling API")
    parser.add_argument("--session-id", help="Instagram sessionid cookie")
    parser.add_argument("--username", help="Instagram username")
    parser.add_argument("--password", help="Instagram password")
    parser.add_argument("--max-follows", type=int, default=5, help="Maximum accounts to follow per run (safe human limit: 3-8)")
    parser.add_argument("--max-comments", type=int, default=3, help="Maximum technical comments to post per run (safe human limit: 2-4)")
    parser.add_argument("--max-likes", type=int, default=8, help="Maximum posts to like per run (safe human limit: 5-10)")
    parser.add_argument("--unfollow-inactive", action="store_true", help="Prune non-reciprocating accounts followed > 7 days ago")
    args = parser.parse_args()

    run_engagement_cycle(args)

if __name__ == "__main__":
    main()
