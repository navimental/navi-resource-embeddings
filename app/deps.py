import os
from fastapi import Header, HTTPException

API_KEY = os.getenv("SIMILARITY_API_KEY")
print("DEBUG EXPECTED KEY:", API_KEY)

def verify_key(x_api_key: str = Header(None)):
    print("DEBUG RECEIVED KEY:", x_api_key)
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
