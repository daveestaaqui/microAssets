"""
Discord Notification Service
==============================
Sends alerts via Discord webhook. Free, instant.
Uses a shared httpx client to avoid connection overhead.

v6.0 Hardened:
 - Retry with exponential backoff (3 attempts)
 - Fallback to local file logging if Discord is unreachable
 - Rate limiting to prevent webhook abuse/banning
 - Message deduplication to prevent alert storms
"""
import httpx
import os
import logging
import asyncio
import hashlib
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
FALLBACK_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "notification_fallback")

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF_S = 1.0
MAX_BACKOFF_S = 10.0

# Rate limiting: max 5 messages per 10 seconds
_recent_sends = []
RATE_LIMIT_WINDOW = 10
RATE_LIMIT_MAX = 5

# Deduplication: prevent identical alerts within 5 minutes
_recent_hashes = {}
DEDUP_WINDOW_S = 300

# Shared client — reuse TCP connections across notifications
_client = None

def _get_client():
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=15.0)
    return _client


def _is_rate_limited():
    """Check if we're sending too fast (Discord will ban the webhook)."""
    global _recent_sends
    now = time.time()
    _recent_sends = [ts for ts in _recent_sends if now - ts < RATE_LIMIT_WINDOW]
    if len(_recent_sends) >= RATE_LIMIT_MAX:
        return True
    _recent_sends.append(now)
    return False


def _is_duplicate(title, message):
    """Check if this exact message was sent recently (prevent alert storms)."""
    global _recent_hashes
    now = time.time()
    # Clean old entries
    _recent_hashes = {k: v for k, v in _recent_hashes.items() if now - v < DEDUP_WINDOW_S}
    
    msg_hash = hashlib.md5(f"{title}:{message[:200]}".encode()).hexdigest()
    if msg_hash in _recent_hashes:
        return True
    _recent_hashes[msg_hash] = now
    return False


def _fallback_log(title, message, color):
    """Write notification to local file when Discord is unreachable."""
    try:
        os.makedirs(FALLBACK_LOG_DIR, exist_ok=True)
        filepath = os.path.join(FALLBACK_LOG_DIR, f"fallback_{datetime.now().strftime('%Y%m%d')}.jsonl")
        import json
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "title": title,
            "message": message[:500],
            "color": color,
            "reason": "discord_unreachable"
        }
        with open(filepath, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        logger.error(f"[NOTIFY] Even fallback logging failed: {e}")


async def send_notification(title: str, message: str, color: int = 0x5865F2, fields: list = None):
    """Send a rich embed notification to Discord with retry + fallback."""
    if not DISCORD_WEBHOOK_URL:
        logger.warning(f"[NOTIFY] No webhook configured. Would have sent: {title}")
        _fallback_log(title, message, color)
        return False
    
    # Deduplication check
    if _is_duplicate(title, message):
        logger.debug(f"[NOTIFY] Deduplicated: {title}")
        return True  # Not an error, just skipped
    
    # Rate limiting check
    if _is_rate_limited():
        logger.warning(f"[NOTIFY] Rate limited. Falling back to local log: {title}")
        _fallback_log(title, message, color)
        return False
    
    embed = {
        "title": title[:256],
        "description": message[:2000],
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {"text": "OmniSuite Worker v6.0"}
    }
    
    if fields:
        embed["fields"] = fields[:25]
    
    # Retry with exponential backoff
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            client = _get_client()
            resp = await client.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
            
            if resp.status_code in (200, 204):
                return True
            elif resp.status_code == 429:
                # Discord rate limit — extract retry_after
                try:
                    retry_data = resp.json()
                    retry_after = retry_data.get("retry_after", 5)
                except Exception:
                    retry_after = 5
                logger.warning(f"[NOTIFY] Discord rate limited. Waiting {retry_after}s...")
                await asyncio.sleep(retry_after)
                continue
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                logger.error(f"[NOTIFY] Attempt {attempt+1} failed: {last_error}")
        except Exception as e:
            last_error = str(e)
            logger.error(f"[NOTIFY] Attempt {attempt+1} error: {e}")
        
        # Exponential backoff
        if attempt < MAX_RETRIES - 1:
            backoff = min(INITIAL_BACKOFF_S * (2 ** attempt), MAX_BACKOFF_S)
            await asyncio.sleep(backoff)
    
    # All retries exhausted — fall back to local log
    logger.error(f"[NOTIFY] All {MAX_RETRIES} attempts failed. Falling back to local log. Last error: {last_error}")
    _fallback_log(title, message, color)
    return False


async def send_alert(message: str):
    """Send a critical alert (red)."""
    await send_notification("🚨 Alert", message, color=0xED4245)


async def send_success(message: str):
    """Send a success notification (green)."""
    await send_notification("✅ Success", message, color=0x57F287)


async def send_info(message: str):
    """Send an informational notification (blue)."""
    await send_notification("ℹ️ Info", message, color=0x5865F2)


async def send_error(message: str):
    """Send a security error notification (red)."""
    await send_notification("🚨 Security Alert", message, color=0xED4245)
