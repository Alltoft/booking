import requests
import os
from dotenv import load_dotenv
import webbrowser
from urllib.parse import parse_qs, urlparse
import base64
import hashlib
import secrets

# Your app's API key (same for all users)
CLIENT_ID = "your_app_api_key_here"  # Replace with your app's API key

def generate_code_verifier():
    """Generate a code verifier for PKCE"""
    token = secrets.token_urlsafe(32)
    return token

def generate_code_challenge(verifier):
    """Generate a code challenge for PKCE"""
    sha256 = hashlib.sha256(verifier.encode('ascii')).digest()
    return base64.urlsafe_b64encode(sha256).decode('ascii').rstrip('=')

def get_oauth_token():
    """Get OAuth2 token for Etsy API access"""
    
    # Generate PKCE code verifier and challenge
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    
    # Define scopes needed for the app
    scopes = [
        'shops_r',           # Read shop data
        'shops_w',           # Write shop data
        'listings_r',        # Read listings
        'listings_w',        # Write listings
        'listings_d'         # Delete listings
    ]
    
    # Construct authorization URL
    auth_url = (
        'https://www.etsy.com/oauth/connect'
        f'?response_type=code'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri=http://localhost:3000/callback'
        f'&scope={" ".join(scopes)}'
        '&code_challenge_method=S256'
        f'&code_challenge={code_challenge}'
    )
    
    # Open the authorization URL in browser
    print("Opening browser for Etsy authorization...")
    webbrowser.open(auth_url)
    
    # Get the authorization code from user
    print("\nAfter authorizing the app, you'll be redirected to a URL.")
    print("Copy and paste that complete URL here (even if it shows an error page):")
    auth_response = input('\nURL: ').strip()
    
    try:
        # Parse the authorization code from the URL
        parsed_url = urlparse(auth_response)
        auth_code = parse_qs(parsed_url.query)['code'][0]
        
        # Exchange authorization code for access token
        token_url = 'https://api.etsy.com/v3/public/oauth/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'redirect_uri': 'http://localhost:3000/callback',
            'code': auth_code,
            'code_verifier': code_verifier
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        tokens = response.json()
        
        # Save tokens to .env file
        with open('.env', 'w') as file:
            file.write(f'ETSY_ACCESS_TOKEN={tokens["access_token"]}\n')
            file.write(f'ETSY_REFRESH_TOKEN={tokens["refresh_token"]}\n')
        
        print("\nSuccess! Your access token has been saved to .env file")
        return tokens
        
    except KeyError:
        print("Error: Could not find authorization code in the URL")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response details: {e.response.text}")
        return None

if __name__ == '__main__':
    print("""
=== Etsy App Authorization ===
This script will help you authorize the app to access your Etsy account.
1. A browser window will open
2. Log in to Etsy if needed
3. Authorize the app
4. Copy the URL you're redirected to
5. Paste it back here
""")
    
    tokens = get_oauth_token()
    
    if tokens:
        print("\n✓ Authorization successful!")
        print("✓ Access token saved to .env file")
        print("✓ You can now use the app with your Etsy account")
    else:
        print("\n✗ Authorization failed. Please try again.") 