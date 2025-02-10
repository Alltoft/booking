from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import os
import json
import requests
import secrets
import hashlib
import base64
import uvicorn
from dotenv import load_dotenv
from urllib.parse import quote

app = FastAPI()

# Load environment variables
load_dotenv()

# Configuration
CLIENT_ID = os.getenv("ETSY_CLIENT_ID")
BASE_URL = "https://etsy-oauth.onrender.com"
REDIRECT_URI = f"{BASE_URL}/callback"
SCOPES = ["shops_r", "shops_w", "listings_r", "listings_w", "listings_d"]

@app.get("/")
def start_auth():
    """Start the OAuth flow"""
    # Generate new PKCE values
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('ascii')).digest()
    ).decode('ascii').rstrip('=')
    state = code_verifier  # Use code_verifier as state to avoid storage

    # Encode redirect URI
    encoded_redirect = quote(REDIRECT_URI, safe='')
    
    auth_url = (
        'https://www.etsy.com/oauth/connect'
        f'?response_type=code'
        f'&redirect_uri={encoded_redirect}'
        f'&client_id={CLIENT_ID}'
        f'&scope={" ".join(SCOPES)}'
        '&code_challenge_method=S256'
        f'&code_challenge={code_challenge}'
        f'&state={state}'
    )
    
    print(f"Auth URL: {auth_url}")  # Debug print
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(code: str = None, state: str = None, error: str = None):
    print(f"Callback received: code={code}, state={state}, error={error}")
    if error:
        return {"error": error}
        
    if not code:
        return {"error": "No authorization code received"}
    
    if not state:
        return {"error": "No state parameter received"}
    
    code_verifier = state
    
    try:
        # Exchange authorization code for access token
        token_url = 'https://api.etsy.com/v3/public/oauth/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'code': code,
            'code_verifier': code_verifier
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        tokens = response.json()
        
        # Instead of writing to .env, return the tokens in the response
        return {
            "message": "Authorization successful!",
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"]
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 