#!/usr/bin/env python3
"""
SporlyWorks — Cryptographic Stripe Webhook Verification Handler
Validates Stripe webhook payloads using HMAC-SHA256 signatures and timestamp tolerances.
"""

import hashlib
import hmac
import json
import logging
import time
from typing import Dict, Any, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("stripe_webhook")

class StripeWebhookError(Exception):
    pass

class SignatureVerificationError(StripeWebhookError):
    pass

def verify_stripe_signature(payload: bytes, sig_header: str, secret: str, tolerance: int = 300) -> Dict[str, Any]:
    """
    Cryptographically verifies Stripe webhook signature using HMAC-SHA256.
    Protects against replay attacks via timestamp tolerance check.
    """
    if not sig_header:
        raise SignatureVerificationError("Missing Stripe-Signature header")

    # Parse signature header: e.g. t=1492774577,v1=5257a869e7ecebeda32affa62cd49231b...
    timestamp = None
    signatures = []

    for item in sig_header.split(","):
        parts = item.strip().split("=", 1)
        if len(parts) == 2:
            key, val = parts[0], parts[1]
            if key == "t":
                try:
                    timestamp = int(val)
                except ValueError:
                    raise SignatureVerificationError("Invalid timestamp in Stripe-Signature")
            elif key == "v1":
                signatures.append(val)

    if timestamp is None:
        raise SignatureVerificationError("Timestamp 't' not found in Stripe-Signature")

    if not signatures:
        raise SignatureVerificationError("No valid 'v1' signatures found in Stripe-Signature")

    # Replay protection
    current_time = int(time.time())
    if abs(current_time - timestamp) > tolerance:
        raise SignatureVerificationError(f"Timestamp outside tolerance range ({abs(current_time - timestamp)}s > {tolerance}s)")

    # Construct signed payload
    signed_payload = f"{timestamp}.".encode("utf-8") + payload
    expected_sig = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()

    # Compare signatures with constant-time equality check
    sig_valid = any(hmac.compare_digest(expected_sig, s) for s in signatures)
    if not sig_valid:
        raise SignatureVerificationError("Signature mismatch: payload authentication failed")

    try:
        return json.loads(payload.decode("utf-8"))
    except Exception as e:
        raise StripeWebhookError(f"Invalid JSON payload: {e}")

def handle_event(event: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Handles verified Stripe events (e.g. checkout.session.completed).
    """
    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        customer_email = data_object.get("customer_details", {}).get("email") or data_object.get("customer_email")
        session_id = data_object.get("id")
        amount_total = data_object.get("amount_total", 0) / 100.0

        logger.info(f"Payment received: ${amount_total:.2f} from {customer_email} (Session: {session_id})")
        # Fulfillment logic: grant portal access to digital dossiers
        return True, f"Fulfillment confirmed for {customer_email}"

    logger.info(f"Ignored unhandled Stripe event type: {event_type}")
    return True, f"Event {event_type} ignored"

if __name__ == "__main__":
    print("SporlyWorks Stripe Webhook Cryptographic Verification Module Loaded.")
