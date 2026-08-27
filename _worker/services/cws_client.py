"""
Chrome Web Store API Client
==============================
Handles OAuth token refresh and CWS API calls.
Uses refresh_token stored in env vars to auto-renew access tokens.

v6.0 Hardened:
 - Retry with exponential backoff on transient errors
 - Circuit breaker to avoid hammering broken APIs
 - Token refresh error handling with logging
 - Request timeout enforcement
"""
import httpx
import os
import logging
import time
import asyncio

logger = logging.getLogger(__name__)

CWS_CLIENT_ID = os.environ.get("CWS_CLIENT_ID", "")
CWS_CLIENT_SECRET = os.environ.get("CWS_CLIENT_SECRET", "")
CWS_REFRESH_TOKEN = os.environ.get("CWS_REFRESH_TOKEN", "")

# In-memory token cache
_token_cache = {"access_token": None, "expires_at": 0}

# Circuit breaker state
_circuit_breaker = {
    "failures": 0,
    "last_failure": 0,
    "state": "CLOSED",       # CLOSED = healthy, OPEN = refusing, HALF_OPEN = testing
    "cooldown_s": 300,       # 5 minutes before retrying after circuit opens
    "failure_threshold": 5,  # Open circuit after this many consecutive failures
}

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2.0
RETRY_BACKOFF_MAX = 30.0

# Retryable HTTP status codes
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


def _check_circuit():
    """Check if the circuit breaker allows requests."""
    cb = _circuit_breaker
    if cb["state"] == "CLOSED":
        return True
    elif cb["state"] == "OPEN":
        if time.time() - cb["last_failure"] > cb["cooldown_s"]:
            cb["state"] = "HALF_OPEN"
            logger.info("[CWS] Circuit breaker: HALF_OPEN — testing connectivity")
            return True
        return False
    elif cb["state"] == "HALF_OPEN":
        return True
    return False


def _record_success():
    """Record a successful request — close circuit if half-open."""
    _circuit_breaker["failures"] = 0
    if _circuit_breaker["state"] != "CLOSED":
        logger.info("[CWS] Circuit breaker: CLOSED (healthy)")
    _circuit_breaker["state"] = "CLOSED"


def _record_failure():
    """Record a failed request — potentially open circuit."""
    cb = _circuit_breaker
    cb["failures"] += 1
    cb["last_failure"] = time.time()
    if cb["failures"] >= cb["failure_threshold"]:
        cb["state"] = "OPEN"
        logger.warning(f"[CWS] Circuit breaker: OPEN after {cb['failures']} consecutive failures. "
                       f"Will retry in {cb['cooldown_s']}s.")


async def _retry_request(method, url, **kwargs):
    """Execute an HTTP request with retry and circuit breaker logic."""
    if not _check_circuit():
        raise Exception(f"Circuit breaker OPEN — CWS API unavailable (last failure {time.time() - _circuit_breaker['last_failure']:.0f}s ago)")
    
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    resp = await client.get(url, **kwargs)
                elif method == "POST":
                    resp = await client.post(url, **kwargs)
                elif method == "PUT":
                    resp = await client.put(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                if resp.status_code in RETRYABLE_STATUS_CODES:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                    logger.warning(f"[CWS] Retryable error (attempt {attempt+1}/{MAX_RETRIES}): {last_error}")
                    
                    # Respect Retry-After header if present
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait = min(float(retry_after), RETRY_BACKOFF_MAX)
                        except ValueError:
                            wait = RETRY_BACKOFF_BASE * (2 ** attempt)
                    else:
                        wait = min(RETRY_BACKOFF_BASE * (2 ** attempt), RETRY_BACKOFF_MAX)
                    
                    await asyncio.sleep(wait)
                    continue
                
                _record_success()
                return resp
                
        except httpx.TimeoutException as e:
            last_error = f"Timeout: {e}"
            logger.warning(f"[CWS] Timeout (attempt {attempt+1}/{MAX_RETRIES}): {e}")
        except httpx.ConnectError as e:
            last_error = f"Connection error: {e}"
            logger.warning(f"[CWS] Connection error (attempt {attempt+1}/{MAX_RETRIES}): {e}")
        except Exception as e:
            last_error = str(e)
            logger.error(f"[CWS] Unexpected error (attempt {attempt+1}/{MAX_RETRIES}): {e}")
        
        # Exponential backoff
        if attempt < MAX_RETRIES - 1:
            wait = min(RETRY_BACKOFF_BASE * (2 ** attempt), RETRY_BACKOFF_MAX)
            await asyncio.sleep(wait)
    
    _record_failure()
    raise Exception(f"CWS API request failed after {MAX_RETRIES} attempts. Last error: {last_error}")


async def get_access_token() -> str:
    """Get a valid access token, refreshing if expired."""
    global _token_cache
    
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]
    
    if not all([CWS_CLIENT_ID, CWS_CLIENT_SECRET, CWS_REFRESH_TOKEN]):
        raise ValueError("CWS OAuth credentials not configured (CWS_CLIENT_ID, CWS_CLIENT_SECRET, CWS_REFRESH_TOKEN)")
    
    resp = await _retry_request(
        "POST",
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CWS_CLIENT_ID,
            "client_secret": CWS_CLIENT_SECRET,
            "refresh_token": CWS_REFRESH_TOKEN,
            "grant_type": "refresh_token"
        },
        timeout=15.0
    )
    
    if resp.status_code != 200:
        raise Exception(f"Token refresh failed: {resp.status_code} {resp.text}")
    
    data = resp.json()
    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600)
    
    logger.info("[CWS] Access token refreshed successfully")
    return _token_cache["access_token"]


async def get_item_status(item_id: str) -> dict:
    """
    Get the status of a CWS item.
    Returns: {"id": ..., "status": "PUBLISHED"|"PENDING_REVIEW"|"DRAFT"|...}
    """
    token = await get_access_token()
    
    resp = await _retry_request(
        "GET",
        f"https://www.googleapis.com/chromewebstore/v1.1/items/{item_id}?projection=DRAFT",
        headers={
            "Authorization": f"Bearer {token}",
            "x-goog-api-version": "2"
        },
        timeout=15.0
    )
    
    if resp.status_code == 200:
        return resp.json()
    else:
        logger.warning(f"[CWS] Failed to get status for {item_id}: {resp.status_code}")
        return {"error": resp.text, "status_code": resp.status_code}


async def try_upload_canary(item_id: str, zip_bytes: bytes) -> dict:
    """
    Try to upload a ZIP to detect if the item is still locked in review.
    Returns: {"uploadState": "SUCCESS"|"FAILURE", ...}
    """
    token = await get_access_token()
    
    resp = await _retry_request(
        "PUT",
        f"https://www.googleapis.com/upload/chromewebstore/v1.1/items/{item_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "x-goog-api-version": "2"
        },
        content=zip_bytes,
        timeout=30.0
    )
    
    return resp.json()


async def publish_item(item_id: str) -> dict:
    """Publish an extension on CWS."""
    token = await get_access_token()
    
    resp = await _retry_request(
        "POST",
        f"https://www.googleapis.com/chromewebstore/v1.1/items/{item_id}/publish",
        headers={
            "Authorization": f"Bearer {token}",
            "x-goog-api-version": "2"
        },
        timeout=15.0
    )
    
    return resp.json()
