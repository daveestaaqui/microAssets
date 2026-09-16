"""
SporlyWorks — Sentinel Security Firewall
Provides institutional defense layers:
1. Prompt Injection Detection & Input Sanitization
2. Server-Side Request Forgery (SSRF) & Private IP Blocking
3. HTML Entity Escaping & Control Character Normalization
4. Immutable Security Audit Logging
"""
from __future__ import annotations

import html
import ipaddress
import json
import re
import socket
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = ROOT / "security" / "sentinel_audit_log.json"

# Prohibited Private/Internal IP Networks
PRIVATE_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

# High-Confidence Prompt Injection Signatures
INJECTION_PATTERNS = [
    re.compile(
        r"\b(?:ignore|disregard|forget|override|bypass)\b.{0,80}"
        r"\b(?:previous|prior|above|system|developer|safety|all)\b.{0,60}"
        r"\b(?:instructions?|prompts?|rules?|polic(?:y|ies)|messages?)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:ignore|bypass|disable)\s+(?:the\s+)?"
        r"(?:guardrails?|safety\s+filters?|security\s+checks?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:reveal|print|show|repeat|dump|expose|extract|send|return)\b.{0,100}"
        r"\b(?:(?:system|developer|hidden|initial)\s+(?:prompt|instructions?)|"
        r"api[\s_-]*keys?|secrets?|access[\s_-]*tokens?|environment\s+variables?)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:api[\s_-]*key|system\s+prompt|developer\s+prompt)\b.{0,60}"
        r"\b(?:reveal|print|send|expose|extract)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:jailbreak|developer\s+mode|do\s+anything\s+now)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\byou\s+are\s+now\b.{0,50}\b(?:unrestricted|unfiltered|DAN)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:<\|(?:im_start|system|developer)\|>|"
        r"\[\s*(?:system|developer)\s*\]|"
        r"</?(?:system|developer)(?:\s[^>]{0,100})?>)",
        re.IGNORECASE,
    ),
    re.compile(r"(?m)^\s*(?:system|developer)\s*:", re.IGNORECASE),
    re.compile(
        r"\b(?:decode|execute|run)\b.{0,60}\b(?:base64|encoded\s+instructions?)\b",
        re.IGNORECASE | re.DOTALL,
    ),
]


def sanitize_input(value: str) -> str:
    """
    Normalizes unicode, strips dangerous control characters,
    and escapes raw HTML entities to prevent XSS/injection.
    """
    if not isinstance(value, str):
        return ""
    # Normalize Unicode NFKC
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    # Strip non-printable control chars except tab and newline
    clean = "".join(
        c for c in value
        if c in "\n\t" or not unicodedata.category(c).startswith("C")
    )
    # HTML escape
    return html.escape(clean, quote=True)


def is_safe_prompt(prompt_text: str) -> tuple[bool, str]:
    """
    Scans user-supplied prompts against known LLM injection patterns.
    Returns (is_safe, violation_reason).
    """
    if not prompt_text or not isinstance(prompt_text, str):
        return True, "Empty prompt"

    normalized = unicodedata.normalize("NFKC", prompt_text)

    for pattern in INJECTION_PATTERNS:
        match = pattern.search(normalized)
        if match:
            reason = f"PROMPT_INJECTION_DETECTED: Matched pattern '{match.group(0)[:60]}'"
            audit_log_event(
                event_type="PROMPT_INJECTION_ATTEMPT",
                severity="HIGH",
                details={"matched_snippet": match.group(0)[:80], "reason": reason}
            )
            return False, reason

    return True, "Safe"


def is_private_ip(ip_str: str) -> bool:
    """Checks if an IP string belongs to any private or restricted range."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in net for net in PRIVATE_NETWORKS)
    except ValueError:
        return True


def validate_url_ssrf(raw_url: str) -> tuple[bool, str]:
    """
    Validates a URL against Server-Side Request Forgery (SSRF).
    Asserts:
    1. Scheme must be http or https.
    2. Hostname must resolve to a valid, publicly routable IP address.
    3. Loopback (127.0.0.1, localhost) and private IP ranges are blocked.
    """
    if not raw_url or not isinstance(raw_url, str):
        return False, "Empty or non-string URL"

    try:
        parsed = urlsplit(raw_url.strip())
    except Exception as e:
        return False, f"Malformed URL: {e}"

    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        return False, f"Prohibited URL scheme: '{scheme}' (only http/https permitted)"

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname in URL"

    hostname_lower = hostname.lower()
    if hostname_lower in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
        audit_log_event(
            event_type="SSRF_PROHIBITED_HOST",
            severity="CRITICAL",
            details={"url": raw_url, "hostname": hostname}
        )
        return False, f"Blocked restricted host: '{hostname}'"

    # Resolve hostname via DNS
    try:
        addr_info = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
        ip_addresses = {info[4][0] for info in addr_info if info[4]}
    except socket.gaierror as e:
        return False, f"DNS resolution failed for '{hostname}': {e}"

    for ip_str in ip_addresses:
        if is_private_ip(ip_str):
            audit_log_event(
                event_type="SSRF_PRIVATE_IP_BLOCKED",
                severity="CRITICAL",
                details={"url": raw_url, "resolved_ip": ip_str}
            )
            return False, f"Host '{hostname}' resolved to private/restricted IP '{ip_str}'"

    return True, "Safe"


def audit_log_event(event_type: str, severity: str, details: dict) -> dict:
    """Appends an event to the sentinel audit log."""
    entry = {
        "event_id": f"SNTL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "severity": severity.upper(),
        "details": details
    }

    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        logs = []
        if LOG_FILE.is_file():
            try:
                logs = json.loads(LOG_FILE.read_text(encoding="utf-8"))
            except Exception:
                logs = []
        logs.append(entry)
        if len(logs) > 1000:
            logs = logs[-1000:]
        LOG_FILE.write_text(json.dumps(logs, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"Sentinel logging error: {e}")

    return entry
