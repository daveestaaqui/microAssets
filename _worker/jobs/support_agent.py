"""
Support Agent — MIGRATED TO CLOUDFLARE
=======================================
Email support has been moved to a Cloudflare Email Worker running on the edge.
This job is now a no-op that logs the migration status.

The Cloudflare worker handles:
  - Inbound email parsing (postal-mime)
  - AI ticket classification (Workers AI)
  - 5 support personas with unique personalities
  - Auto-replies with HTML signatures
  - Auto-refunds via Stripe REST API
  - Bug logging to KV
  - Escalation forwarding

See: _cloudflare_email_worker/ for the active implementation.
"""
import logging

logger = logging.getLogger(__name__)


async def run():
    """No-op — email support is now handled by Cloudflare Email Worker."""
    logger.info(
        "[SUPPORT AGENT] ☁️ Email support has migrated to Cloudflare Email Workers. "
        "This Railway job is now a no-op. See _cloudflare_email_worker/ for the active system."
    )
