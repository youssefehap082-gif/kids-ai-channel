"""
scripts/utils/http.py
HTTP utilities with retry/backoff and structured logging.
No external secrets here. Use environment variables for keys.
"""

import time
import logging
import requests
from typing import Any, Dict, Optional

logger = logging.getLogger("kids_ai.http")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(ch)


class HTTPError(Exception):
    pass


def request_with_retry(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    timeout: int = 15,
    retries: int = 3,
    backoff_factor: float = 1.0,
    allowed_statuses: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Make an HTTP request with retries and exponential backoff.
    Returns: dict with keys: status_code, headers, text, json (if parsable)
    Raises HTTPError on final failure.
    """
    attempt = 0
    last_exc = None
    allowed_statuses = allowed_statuses or []

    while attempt <= retries:
        try:
            logger.debug("HTTP %s %s attempt=%d", method.upper(), url, attempt)
            resp = requests.request(method=method, url=url, headers=headers, params=params,
                                    json=json, data=data, timeout=timeout)
            logger.debug("Response status: %s for %s", resp.status_code, url)

            if resp.status_code >= 500 and attempt < retries:
                # server error -> retry
                logger.warning("Server error %s on %s (attempt %d). Retrying...", resp.status_code, url, attempt)
                raise HTTPError(f"Server error {resp.status_code}")

            if resp.status_code >= 400 and resp.status_code not in allowed_statuses:
                # client error and not allowed -> raise
                logger.error("Client error %s on %s: %s", resp.status_code, url, resp.text[:400])
                raise HTTPError(f"Client error {resp.status_code}: {resp.text[:200]}")

            # success-ish
            out = {"status_code": resp.status_code, "headers": dict(resp.headers), "text": resp.text}
            try:
                out["json"] = resp.json()
            except Exception:
                out["json"] = None
            return out

        except (requests.Timeout, requests.ConnectionError, HTTPError) as exc:
            last_exc = exc
            sleep = backoff_factor * (2 ** attempt)
            logger.warning("Request failed (%s). Backing off %.1fs and retrying (attempt %d/%d).", exc, sleep, attempt, retries)
            time.sleep(sleep)
            attempt += 1

    logger.error("All retries failed for %s %s: %s", method, url, last_exc)
    raise HTTPError(f"Failed request {method} {url}: {last_exc}")


# convenience wrappers
def get(*args, **kwargs):
    return request_with_retry("GET", *args, **kwargs)


def post(*args, **kwargs):
    return request_with_retry("POST", *args, **kwargs)
