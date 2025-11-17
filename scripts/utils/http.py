import requests
import time

def safe_request(url, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        try:
            print(f"Requesting: {url} (attempt {attempt})")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Request failed: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                return {"error": str(e)}
