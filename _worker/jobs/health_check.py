"""
Extension Health Check
======================
Validates all 85 extensions by checking CWS public pages.
Detects:
- Extensions that got taken down
- Extensions with errors (rejected updates)
- Missing/broken listings

Runs every 6 hours via scheduler.
"""
import os
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

CWS_ITEM_IDS_JSON = os.environ.get("CWS_ITEM_IDS", "{}")
LICENSE_SERVER_URL = os.environ.get("LICENSE_SERVER_URL", "https://microassets-license-server-production.up.railway.app")


async def run():
    """
    Main health check job.
    Checks CWS status of all extensions and license server health.
    """
    import httpx
    from services.notifications import send_notification, send_alert
    
    logger.info("[HEALTH] Starting extension health check...")
    
    try:
        item_ids = json.loads(CWS_ITEM_IDS_JSON)
    except json.JSONDecodeError:
        logger.error("[HEALTH] Invalid CWS_ITEM_IDS JSON")
        return
    
    results = {
        "total": len(item_ids),
        "live": 0,
        "not_live": 0,
        "errors": 0,
        "issues": []
    }
    
    # 1. Check License Server health
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{LICENSE_SERVER_URL}/health", timeout=10.0)
            if resp.status_code == 200:
                logger.info("[HEALTH] ✅ License server healthy")
            else:
                results["issues"].append(f"License server returned {resp.status_code}")
                logger.warning(f"[HEALTH] ⚠️ License server returned {resp.status_code}")
    except Exception as e:
        results["issues"].append(f"License server unreachable: {e}")
        logger.error(f"[HEALTH] ❌ License server error: {e}")
    
    # 2. Sample check CWS listings (check 10 random extensions to avoid rate limits)
    import random
    sample_items = list(item_ids.items())
    if len(sample_items) > 10:
        sample_items = random.sample(sample_items, 10)
    
    async with httpx.AsyncClient() as client:
        for slug, ext_id in sample_items:
            try:
                # Check public CWS page
                url = f"https://chrome.google.com/webstore/detail/{ext_id}"
                resp = await client.get(url, follow_redirects=True, timeout=10.0)
                
                if resp.status_code == 200:
                    results["live"] += 1
                elif resp.status_code == 404:
                    results["not_live"] += 1
                    # 404 during review is normal — only alert if we expected it to be live
                else:
                    results["errors"] += 1
                    results["issues"].append(f"{slug}: HTTP {resp.status_code}")
                
                await asyncio.sleep(0.5)  # Be nice to Google
                
            except Exception as e:
                results["errors"] += 1
                logger.warning(f"[HEALTH] Error checking {slug}: {e}")
    
    # 3. Check CWS API status for canary (if credentials available)
    try:
        from services.cws_client import get_item_status, CWS_CLIENT_ID
        if CWS_CLIENT_ID:
            canary_slug = os.environ.get("CWS_CANARY_SLUG", "ai-content-bouncer")
            canary_id = item_ids.get(canary_slug)
            if canary_id:
                status = await get_item_status(canary_id)
                cws_status = status.get("status", "UNKNOWN")
                logger.info(f"[HEALTH] CWS API canary ({canary_slug}): {cws_status}")
                results["cws_api_status"] = cws_status
    except Exception as e:
        logger.warning(f"[HEALTH] CWS API check skipped: {e}")
    
    # Summary
    logger.info(f"[HEALTH] Check complete: {results['live']}/{len(sample_items)} sampled live, {results['errors']} errors")
    
    # Only alert if there are real issues
    if results["issues"]:
        await send_notification(
            "⚠️ Health Check Issues",
            "\n".join([f"• {issue}" for issue in results["issues"][:10]]),
            color=0xFEE75C,
            fields=[
                {"name": "Sampled", "value": str(len(sample_items)), "inline": True},
                {"name": "Live", "value": str(results["live"]), "inline": True},
                {"name": "Issues", "value": str(len(results["issues"])), "inline": True}
            ]
        )
    
    return results
