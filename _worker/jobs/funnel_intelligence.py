"""
Funnel Intelligence Job
======================
Monitors the conversion funnel from the license server and 
orchestrates marketing/strategic responses.
"""
import os
import json
import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

LICENSE_SERVER_URL = os.environ.get("LICENSE_SERVER_URL", "https://microassets-license-server-production.up.railway.app")
ADMIN_SECRET = os.environ.get("CEO_INBOX_SECRET", "") # Re-using secret for admin metrics

async def run():
    logger.info("[FUNNEL] Starting conversion intelligence audit...")
    
    if not ADMIN_SECRET:
        logger.error("[FUNNEL] No ADMIN_SECRET (CEO_INBOX_SECRET) found. Skipping.")
        return

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{LICENSE_SERVER_URL}/metrics",
                headers={"X-Admin-Key": ADMIN_SECRET},
                timeout=15.0
            )
            
            if resp.status_code != 200:
                logger.error(f"[FUNNEL] Failed to fetch metrics: {resp.status_code}")
                return
                
            data = resp.json()
            
        # Process conversion intelligence
        total_users = data.get("total_users", 0)
        pro_users = data.get("pro_users", 0)
        conv_rate = data.get("conversion_rate", 0)
        
        logger.info(f"[FUNNEL] Snapshot: {total_users} Users | {pro_users} Pro | {conv_rate}% Conv")
        
        # Check for drop-offs in the funnel
        funnel = data.get("funnel", {})
        vis = funnel.get("visit_landing", 0)
        reg = funnel.get("register_user", 0)
        suc = funnel.get("success_conversion", 0)
        
        if vis > 0 and (reg / vis) < 0.10:
            logger.warning("[FUNNEL] CRITICAL DROP-OFF: Landing-to-Registration is below 10%.")
            # In a real scenario, we'd trigger the MarketingAgent to adjust index.html copy
            
        if reg > 0 and (suc / reg) < 0.02:
            logger.warning("[FUNNEL] CRITICAL DROP-OFF: Registration-to-Paid is below 2%.")
            # Trigger Pro Suite GTM strategy
            
        # Save intelligence snapshot for the Board Coordinator
        intelligence_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "funnel_intelligence.json")
        with open(intelligence_path, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "metrics": data,
                "alerts": [
                    "Low L-to-R conversion" if vis > 0 and (reg/vis) < 0.10 else None,
                    "Low R-to-P conversion" if reg > 0 and (suc/reg) < 0.02 else None
                ]
            }, f, indent=2)
            
        logger.info("[FUNNEL] Intelligence audit complete.")
        
    except Exception as e:
        logger.error(f"[FUNNEL] Error during intelligence audit: {e}")
