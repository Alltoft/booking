import requests
import os
from dotenv import load_dotenv

load_dotenv()

def add_listing_sandbox(title, description, price, quantity, materials, tags):
    """Create a new listing in Etsy sandbox environment"""
    
    shop_id = os.getenv('ETSY_SHOP_ID')
    url = f"https://api.etsy.com/v3/application/shops/{shop_id}/listings"
    
    headers = {
        "x-api-key": os.getenv('ETSY_API_KEY'),
        "Authorization": f"Bearer {os.getenv('ETSY_ACCESS_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    # Validate inputs
    if len(tags) > 13:
        return {"error": "Maximum 13 tags allowed"}
    if len(title) > 140:
        return {"error": "Title must be 140 characters or less"}
    
    data = {
        "title": title,
        "description": description,
        "price": {
            "amount": int(float(price) * 100),  # Convert to cents
            "divisor": 100,
            "currency_code": "USD"
        },
        "quantity": quantity,
        "who_made": "i_did",
        "is_supply": False,
        "when_made": "made_to_order",
        "taxonomy_id": 11111,  # Replace with correct taxonomy ID for digital products
        "type": "download",
        "state": "draft",
        "materials": materials[:13],  # Max 13 materials
        "tags": tags,
        "should_auto_renew": False,
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e), "details": getattr(e.response, 'text', '')}

# if __name__ == "__main__":
#     # Test data
#     test_data = {
#         "title": "Digital Product Test",
#         "description": "This is a test digital product listing.",
#         "price": 9.99,
#         "quantity": 999,
#         "materials": ["digital", "PDF"],
#         "tags": ["digital", "ebook", "PDF", "instant download"]
#     }
    
#     result = add_listing_sandbox(**test_data)
#     print(result)
