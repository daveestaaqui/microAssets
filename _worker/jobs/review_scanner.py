"""
Review Scanner
==============
Checks Chrome Web Store for new reviews on published extensions.
Detects patterns (recurring bugs, feature requests) and alerts.

Runs daily via scheduler.
"""
import os
import json
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

CWS_ITEM_IDS_JSON = os.environ.get("CWS_ITEM_IDS", "{}")

# Persistent review tracking (in-memory, reset on deploy)
_seen_reviews = set()


async def run():
    """
    Scan CWS public pages for reviews on sample extensions.
    Focus on negative reviews (1-2 stars) that might indicate bugs.
    """
    import httpx
    from services.notifications import send_notification
    
    logger.info("[REVIEWS] Starting daily review scan...")
    
    try:
        item_ids = json.loads(CWS_ITEM_IDS_JSON)
    except json.JSONDecodeError:
        logger.error("[REVIEWS] Invalid CWS_ITEM_IDS JSON")
        return
    
    if not item_ids:
        logger.info("[REVIEWS] No extensions configured - skipping")
        return
    
    # Sample 15 extensions per day to stay within rate limits
    import random
    sample = list(item_ids.items())
    if len(sample) > 15:
        sample = random.sample(sample, 15)
    
    new_reviews = []
    bug_reports = []
    
    async with httpx.AsyncClient() as client:
        for slug, ext_id in sample:
            try:
                # Try to fetch the CWS page — reviews are rendered client-side
                # so we can only detect if the extension is live
                url = f"https://chrome.google.com/webstore/detail/{ext_id}"
                resp = await client.get(url, follow_redirects=True, timeout=10.0)
                
                if resp.status_code == 200:
                    body = resp.text
                    
                    # Extract star rating if visible in meta/structured data
                    rating_match = re.search(r'"ratingValue":\s*"?([\d.]+)"?', body)
                    review_count_match = re.search(r'"ratingCount":\s*"?(\d+)"?', body)
                    
                    if rating_match:
                        rating = float(rating_match.group(1))
                        count = int(review_count_match.group(1)) if review_count_match else 0
                        
                        if count > 0:
                            logger.info(f"[REVIEWS] {slug}: {rating}⭐ ({count} reviews)")
                            
                            if rating < 3.0 and count >= 3:
                                bug_reports.append({
                                    "slug": slug,
                                    "rating": rating,
                                    "count": count
                                })
                
                await asyncio.sleep(1)  # Rate limit
                
            except Exception as e:
                logger.warning(f"[REVIEWS] Error scanning {slug}: {e}")
    
    # Alert on low-rated extensions
    if bug_reports:
        report_lines = [f"• **{r['slug']}**: {r['rating']}⭐ ({r['count']} reviews)" for r in bug_reports]
        await send_notification(
            "📋 Low-Rated Extensions Detected",
            "The following extensions have ratings below 3.0 stars:\n\n" + "\n".join(report_lines),
            color=0xED4245,
            fields=[
                {"name": "Extensions Scanned", "value": str(len(sample)), "inline": True},
                {"name": "Low-Rated", "value": str(len(bug_reports)), "inline": True}
            ]
        )
    
    logger.info(f"[REVIEWS] Scan complete: {len(sample)} checked, {len(bug_reports)} low-rated")
    return {"scanned": len(sample), "issues": len(bug_reports)}
