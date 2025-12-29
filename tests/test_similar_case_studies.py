import requests
from child_situation_examples import TEST_FAMILY_1

API_URL = "http://127.0.0.1:8001/similar-case-studies/similar"
API_KEY = "super-secret-local-key"

TEST_PAYLOAD = TEST_FAMILY_1  # swap with 2 or 3

if __name__ == "__main__":
    res = requests.post(
        API_URL,
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json=TEST_PAYLOAD
    )

    print("Status:", res.status_code)
    print("Response:", res.json())
