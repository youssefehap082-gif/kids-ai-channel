import sys
import os

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from scripts.generate_script import generate_facts
from scripts.utils.http import safe_request


def main():
    print("=== AI Kids Channel Pipeline Runner ===")

    # 1) Generate script
    facts = generate_facts()
    print("Generated Script Content:")
    print("------------------------")
    print(facts)

    # 2) Example web request using safe_request()
    print("\nTesting HTTP provider system...")
    test_url = "https://httpbin.org/get"
    response = safe_request(test_url)

    print("HTTP Test Response:")
    print(response)

    print("\nPipeline finished successfully.")


if __name__ == "__main__":
    main()
