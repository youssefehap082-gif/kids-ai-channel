import requests
import time
import logging
import json
import os

# Load configuration manually because it is a JSON file, not a Python file
try:
    # We use a relative path assuming the script runs from the project root
    config_path = os.path.join(os.getcwd(), "config", "retry_config.json")
    with open(config_path, "r") as f:
        rc = json.load(f)
except Exception as e:
    logging.warning(f"Could not load retry_config.json: {e}. Using defaults.")
    # Fallback default if file is missing
    rc = {"max_retries": 3, "timeout_seconds": 30, "backoff_factor": 2}

def fetch_with_retry(url, headers=None, params=None, method="GET"):
    retries = 0
    while retries < rc.get('max_retries', 3):
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=rc.get('timeout_seconds', 30))
            else:
                response = requests.post(url, headers=headers, json=params, timeout=rc.get('timeout_seconds', 30))
            
            response.raise_for_status()
            return response
        except Exception as e:
            logging.warning(f"Request failed ({retries+1}/{rc.get('max_retries', 3)}): {e}")
            retries += 1
            time.sleep(rc.get('backoff_factor', 2) ** retries)
    
    logging.error(f"Failed to fetch {url} after all retries.")
    return None