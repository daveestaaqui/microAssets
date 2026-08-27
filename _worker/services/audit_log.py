"""
Enterprise Audit Logger
========================
Append-only structured JSONL audit trail for all security-relevant events.
Every refund, bug log, email processed, and patch applied is recorded
with timestamps and context for forensic traceability.
"""
import os
import json
import logging
import datetime

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
AUDIT_LOG_PATH = os.path.join(DATA_DIR, "audit_log.jsonl")


def log_event(event_type: str, details: dict, source: str = "worker"):
    """
    Append a single structured JSON event to the audit log.
    
    event_type: e.g., 'REFUND_PROCESSED', 'BUG_LOGGED', 'EMAIL_RECEIVED',
                'PATCH_APPLIED', 'RATE_LIMITED', 'PATH_TRAVERSAL_BLOCKED',
                'FACTORY_BUILD', 'ESCALATION_SENT', 'STARTUP'
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    
    entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "event": event_type,
        "source": source,
        **details
    }
    
    try:
        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        logger.error(f"[AUDIT] Failed to write audit log entry: {e}")


def log_security_event(event_type: str, details: dict):
    """Convenience wrapper for security-specific events."""
    details["severity"] = "SECURITY"
    log_event(event_type, details, source="security")


def get_recent_events(event_type: str = None, limit: int = 50) -> list:
    """Read recent audit events, optionally filtered by type."""
    if not os.path.exists(AUDIT_LOG_PATH):
        return []
    
    events = []
    try:
        with open(AUDIT_LOG_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        if event_type is None or entry.get("event") == event_type:
                            events.append(entry)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.error(f"[AUDIT] Failed to read audit log: {e}")
    
    return events[-limit:]
