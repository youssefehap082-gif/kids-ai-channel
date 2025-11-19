import requests
import time
import logging
from config.retry_config import retry_config as rc

def fetch_with_retry(url, headers=None, params=None, method="GET"):
    retries = 0
    while retries < rc['max_retries']:
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=rc['timeout_seconds'])
            else:
                response = requests.post(url, headers=headers, json=params, timeout=rc['timeout_seconds'])
            
            response.raise_for_status()
            return response
        except Exception as e:
            logging.warning(f"Request failed ({retries+1}/{rc['max_retries']}): {e}")
            retries += 1
            time.sleep(rc['backoff_factor'] ** retries)
    
    logging.error(f"Failed to fetch {url} after all retries.")
    return None
