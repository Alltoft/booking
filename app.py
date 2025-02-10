from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import os
import json
from datetime import datetime, timedelta
import requests
import secrets
import hashlib
import base64
import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Load environment variables
load_dotenv()

# Configuration
CLIENT_ID = os.getenv("ETSY_CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://etsy-oauth.onrender.com/callback")
SCOPES = ["shops_r", "shops_w", "listings_r", "listings_w", "listings_d"]

# Store OAuth state
class OAuthState:
    code_verifier = None
    code_challenge = None
    state = None

oauth_state = OAuthState()

# Add security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:3000",  # If you have a frontend running on port 3000
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def start_auth():
    """Start the OAuth flow"""
    # Generate new PKCE values and state for this request
    oauth_state.code_verifier = secrets.token_urlsafe(32)
    oauth_state.code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(oauth_state.code_verifier.encode('ascii')).digest()
    ).decode('ascii').rstrip('=')
    oauth_state.state = secrets.token_urlsafe(16)

    auth_url = (
        'https://www.etsy.com/oauth/connect'
        f'?response_type=code'
        f'&redirect_uri={REDIRECT_URI}'
        f'&client_id={CLIENT_ID}'
        f'&scope={" ".join(SCOPES)}'
        '&code_challenge_method=S256'
        f'&code_challenge={oauth_state.code_challenge}'
        f'&state={oauth_state.state}'
    )
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(code: str = None, state: str = None, error: str = None):
    """Handle the OAuth callback"""
    if error:
        return {"error": error}
        
    if not code:
        return {"error": "No authorization code received"}
    
    if state != oauth_state.state:
        return {"error": "Invalid state parameter"}
    
    try:
        # Exchange authorization code for access token
        token_url = 'https://api.etsy.com/v3/public/oauth/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'code': code,
            'code_verifier': oauth_state.code_verifier
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        tokens = response.json()
        
        # Save tokens to .env file
        # Read existing content
        with open('.env', 'r') as file:
            lines = file.readlines()

        # Remove existing tokens if present
        lines = [line for line in lines if not line.startswith(('ETSY_ACCESS_TOKEN=', 'ETSY_REFRESH_TOKEN='))]

        # Write back all content plus new tokens
        with open('.env', 'w') as file:
            file.writelines(lines)
            file.write(f'ETSY_ACCESS_TOKEN={tokens["access_token"]}\n')
            file.write(f'ETSY_REFRESH_TOKEN={tokens["refresh_token"]}\n')
        
        return {"message": "Authorization successful! You can close this window."}
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("""
=== Etsy App Authorization ===
1. Open your browser and go to: http://localhost:8000
2. Log in to Etsy if needed
3. Authorize the app
4. The tokens will be automatically saved to your .env file
""")
    uvicorn.run(app, host="0.0.0.0", port=port) 