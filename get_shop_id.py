import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Your app's API key (same for all users)
CLIENT_ID = "your_app_api_key_here"  # Replace with your app's API key

def get_my_shops():
    """Fetch shops for the authenticated user (based on their access token)"""
    
    access_token = os.getenv('ETSY_ACCESS_TOKEN')
    if not access_token:
        return {
            "status": "error",
            "message": "No access token found. Please run get_oauth_token.py first to authorize your account."
        }
    
    try:
        # First, get the authenticated user's details
        user_response = requests.get(
            'https://api.etsy.com/v3/application/users/me',
            headers={
                'x-api-key': CLIENT_ID,
                'Authorization': f"Bearer {access_token}"
            }
        )
        user_response.raise_for_status()
        user_data = user_response.json()
        
        print(f"\nAuthenticated as: {user_data['user']['login_name']}")
        print(f"User ID: {user_data['user']['user_id']}")
        
        # Then get their shops
        shops_response = requests.get(
            'https://api.etsy.com/v3/application/users/me/shops',
            headers={
                'x-api-key': CLIENT_ID,
                'Authorization': f"Bearer {access_token}"
            }
        )
        shops_response.raise_for_status()
        
        shops = shops_response.json()
        return {
            "status": "success",
            "user": user_data['user'],
            "shops": shops['shops']
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": str(e),
            "details": getattr(e.response, 'text', '')
        }

if __name__ == "__main__":
    result = get_my_shops()
    
    if result["status"] == "success":
        if not result["shops"]:
            print(f"\n{result['user']['login_name']}, you don't have any shops on Etsy yet.")
        else:
            print(f"\nShops for {result['user']['login_name']}:")
            print("-" * 50)
            for shop in result["shops"]:
                print(f"Shop Name: {shop['shop_name']}")
                print(f"Shop ID: {shop['shop_id']}")
                print(f"Creation Date: {shop['create_date']}")
                print(f"URL: https://www.etsy.com/shop/{shop['shop_name']}")
                print("-" * 50)
    else:
        print(f"Error: {result['message']}") 