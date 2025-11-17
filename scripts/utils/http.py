"""
scripts/utils/http.py
HTTP utilities: request_with_retry + lightweight wrappers.
Used by providers to centralize retry/backoff and logging.
"""

import time
import logging
import requests
from typing import Any, Dict, Optional

logger = logging.getLogger("kids_ai.http")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)

class HTTPError(Exception):
    pass

def request_with_retry(
    method: str,
    url: str,
    headers: Optional[Dict[str,str]] = None,
    params: Optional[Dict[str,Any]] = None,
    json: Optional[Dict[str,Any]] = None,
    data: Optional[Any] = None,
    timeout: int = 15,
    retries: int = 3,
    backoff_factor: float = 1.0,
    allowed_statuses: Optional[list] = None,
) -> Dict[str,Any]:
    attempt = 0
    allowed_statuses = allowed_statuses or []
    last_exc = None
    while attempt <= retries:
        try:
            logger.debug("HTTP %s %s attempt=%d", method.upper(), url, attempt)
            resp = requests.request(method=method, url=url, headers=headers, params=params, json=json, data=data, timeout=timeout)
            logger.debug("Status %s for %s", resp.status_code, url)
            if resp.status_code >= 500 and attempt < retries:
                raise HTTPError(f"Server error {resp.status_code}")
            if resp.status_code >= 400 and resp.status_code not in allowed_statuses:
                raise HTTPError(f"Client error {resp.status_code}: {resp.text[:200]}")
            out = {"status_code": resp.status_code, "headers": dict(resp.headers), "text": resp.text}
            try:
                out["json"] = resp.json()
            except Exception:
                out["json"] = None
            return out
        except (requests.Timeout, requests.ConnectionError, HTTPError) as exc:
            last_exc = exc
            sleep = backoff_factor * (2 ** attempt)
            logger.warning("Request failed (%s). Backoff %.1fs", exc, sleep)
            time.sleep(sleep)
            attempt += 1
    logger.error("All retries failed for %s %s: %s", method, url, last_exc)
    raise HTTPError(f"Failed request {method} {url}: {last_exc}")

def get(url, **kwargs):
    return request_with_retry("GET", url, **kwargs)

def post(url, **kwargs):
    return request_with_retry("POST", url, **kwargs)
