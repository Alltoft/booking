from fastapi import FastAPI, Request, Query
from fastapi.responses import RedirectResponse
import os
import json
import requests
import secrets
import hashlib
import base64
import httpx
import uvicorn
from typing import List
from dotenv import load_dotenv
from urllib.parse import quote
from scraper import download_pdf, extract_title
from searchbook import search_book_by_title_openlibrary
from fastapi.middleware.cors import CORSMiddleware  # Add this import
# ...existing imports...

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load environment variables
load_dotenv()

# Configuration
CLIENT_ID = os.getenv("ETSY_CLIENT_ID")
REDIRECT_URI = "http://localhost:8000/callback"  # Always use localhost
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
        token_url = 'https://openapi.etsy.com/v3/public/oauth/token'
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
        print(f"Tokens: {tokens}")
        # Update tokens in .env file
        try:
            with open('.env', 'r') as file:
                lines = file.readlines()
            
            # Remove existing tokens
            lines = [line for line in lines if not line.startswith(('ETSY_ACCESS_TOKEN=', 'ETSY_REFRESH_TOKEN='))]
            
            # Add new tokens
            with open('.env', 'w') as file:
                file.writelines(lines)
                file.write(f'ETSY_ACCESS_TOKEN={tokens["access_token"]}\n')
                file.write(f'ETSY_REFRESH_TOKEN={tokens["refresh_token"]}\n')
        except:
            pass
        
        return {"message": "Authorization successful! You can close this window."}
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}
    
@app.get("/refresh")
async def refresh_token():
    try:
        # Load refresh token from .env file
        with open('.env', 'r') as file:
            lines = file.readlines()
        
        refresh_token = next(line for line in lines if line.startswith('ETSY_REFRESH_TOKEN=')).split('=')[1].strip()
        
        # Exchange refresh token for new access token
        token_url = 'https://api.etsy.com/v3/public/oauth/token'
        data = {
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'refresh_token': refresh_token
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        tokens = response.json()
        
        # Update access token in .env file
        try:
            with open('.env', 'r') as file:
                lines = file.readlines()
            
            # Remove existing access token
            lines = [line for line in lines if not line.startswith('ETSY_ACCESS_TOKEN=')]
            
            # Add new access token
            with open('.env', 'w') as file:
                file.writelines(lines)
                file.write(f'ETSY_ACCESS_TOKEN={tokens["access_token"]}\n')
        except:
            pass
        
        return {"message": "Token refreshed successfully!"}
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}

@app.get("/get-user")
def get_user():
    try:
        
        # Load access token from .env file
        with open('.env', 'r') as file:
            lines = file.readlines()

        access_token = next(line for line in lines if line.startswith('ETSY_ACCESS_TOKEN=')).split('=')[1].strip()
        x_api_key = os.getenv("ETSY_CLIENT_ID")
        print('access_token: ', access_token, '\nx_api_key: ', x_api_key)
        
        # Get user details
        user_url = 'https://openapi.etsy.com/v3/application/users/me'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': x_api_key
        }
        
        response = requests.get(user_url, headers=headers)
        response.raise_for_status()
        
        user = response.json()
        
        return {"shop_id": user['shop_id']}
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}
    
# @app.get("/get-taxonomy")
# def get_taxonomy():
#     try:
#         x_api_key = os.getenv("ETSY_CLIENT_ID")
        
#         # Get taxonomy details
#         taxonomy_url = 'https://openapi.etsy.com/v3/application/seller-taxonomy/nodes'
#         headers = {'x-api-key': x_api_key}
        
#         response = requests.get(taxonomy_url, headers=headers)
#         response.raise_for_status()
        
#         taxonomy = response.json()
        
#         return taxonomy
        
#     except requests.exceptions.RequestException as e:
#         return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}

@app.get("/create-listing")
def create_listing(shop_id, title, description):
    try:
        # Load access token from .env file
        with open('.env', 'r') as file:
            lines = file.readlines()
        
        access_token = next(line for line in lines if line.startswith('ETSY_ACCESS_TOKEN=')).split('=')[1].strip()
        
        # Create a new listing
        listing_url = f'https://openapi.etsy.com/v3/application/shops/{shop_id}/listings'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': CLIENT_ID,
            'Content-Type': 'application/json'
        }
        
        data = {
            'title': title,
            'description': description,
            'price': 99999,
            'quantity': 999,
            'who_made': 'i_did',
            'when_made': 'made_to_order',
            'is_supply': False,
            'type': 'download',
            'materials': ['digital', 'PDF'],
            'tags': ['digital', 'ebook', 'PDF', 'instant download'],
            'should_auto_renew': False,
            'taxonomy_id': 324,
            'state': 'draft'
        }
        
        response = requests.post(listing_url, headers=headers, json=data)
        response.raise_for_status()
        
        listing = response.json()
        
        return {"listing_id": listing['listing_id']}
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}
    
# @app.get("/get-book-pdf")                                           }
# def get_book_pdf(book_url='https://www.gutenberg.org/ebooks/1342'): }
#     try:                                                            }
#         # Download PDF                                              }
#         pdf = download_pdf(book_url)                                }
#         title = extract_title(book_url)                             }     A METHOD TO SEE LATER DON'T DELETE IT
#                                                                     }
#         return {"title": title, "pdf": pdf}                         }
#                                                                     }
#     except Exception as e:                                          }
#         return {"error": str(e)}                                    }
#                                                                     }

@app.get("/get-book-pdf")
def get_book_pdf(book_url):
    try:
        # Download PDF
        pdf = download_pdf(book_url)
        title = extract_title(book_url)
        
        return {"title": title, "pdf": pdf}
        
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/search-book")
def search_book(title):
    try:
        # Search for book
        book = search_book_by_title_openlibrary(title)
        return book["data"]
    
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/generate-description")
def generate_description(
    title: str = Query(None),
    authors: List[str] = Query(None),
    publish_year: str = Query(None),
    publishers: List[str] = Query(None),
    subjects: List[str] = Query(None)
):

    try:
        # Generate description
        description_parts = [
            f"Introducing {title}" if title else "",
            f", a captivating and transformative work by {authors}." if authors else "",
            f" Published in {publish_year}" if publish_year != ['N/A'] else "",
            f" by {publishers}" if publishers != ['N/A'] else "",
            ", this book invites readers to embark on a journey of discovery and inspiration. With its engaging narrative and insightful perspectives,",
            f" {title} explores themes of {subjects} and offers practical wisdom to enhance your everyday life." if subjects else f" {title} offers practical wisdom to enhance your everyday life."
        ]

        # Join the non-empty parts into a single string
        description = ''.join(part for part in description_parts if part)

        descriptions = (
            f"Title: {title}\n"
            f"Author: {authors}\n\n"
            f"{description}\n\n"
        )
        
        return {"description": descriptions}
        
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/upload-listing-image")
async def upload_listing_image(shop_id=57595253, listing_id=1873746497, image_url='https://covers.openlibrary.org/b/id/1932116-L.jpg'):
    try:
        # Load access token from .env file
        with open('.env', 'r') as file:
            lines = file.readlines()

        access_token = next(line for line in lines if line.startswith('ETSY_ACCESS_TOKEN=')).split('=')[1].strip()

        # Get image data directly from URL
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(image_url)
            response.raise_for_status()

        image_upload_url = f'https://openapi.etsy.com/v3/application/shops/{shop_id}/listings/{listing_id}/images'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': CLIENT_ID,
        }

        # Create files parameter for multipart form data
        files = {
            'image': ('image.jpg', response.content, 'image/jpeg')
        }

        # Use requests to upload the image
        response = requests.post(image_upload_url, headers=headers, files=files)
        response.raise_for_status()

        image = response.json()
        return {"image_id": image['listing_image_id']}
    
    except (requests.exceptions.RequestException, httpx.HTTPError) as e:
        return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}
    
@app.get("/upload-listing-file")
async def upload_listing_file(shop_id, listing_id, file_name):
    try:
        # Load access token from .env file
        with open('.env', 'r') as file:
            lines = file.readlines()

        access_token = next(line for line in lines if line.startswith('ETSY_ACCESS_TOKEN=')).split('=')[1].strip()

        # Get file data
        with open(file_name, 'rb') as file:
            file_data = file.read()

        file_upload_url = f'https://openapi.etsy.com/v3/application/shops/{shop_id}/listings/{listing_id}/files'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': CLIENT_ID,
        }
        
        # Remove file extension and underscores from file name take only what is before :
        name = file_name.split(':')[0].replace('_', ' ')

        # Create files parameter for multipart form data
        files = {
            'file': ('file.pdf', file_data, 'application/pdf'),
        }
        
        # Add name as form data
        data = {
            'name': name
        }

        # Use requests to upload the file with both files and form data
        response = requests.post(file_upload_url, headers=headers, files=files, data=data)
        response.raise_for_status()

        file = response.json()
        return {"file_id": file['listing_file_id'], "name": name}
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}
    
@app.get("/delete-pdf")
def delete_pdf(file_name='Living_in_the_Light:_A_guide_to_personal_transformation.pdf'):
    try:
        os.remove(file_name)
        return {"message": "PDF deleted successfully!"}
    
    except Exception as e:
        return {"error": str(e)}


@app.get("/get-listings")
def get_listings(shop_id=57595253):
    try:
        # Load access token from .env file
        with open('.env', 'r') as file:
            lines = file.readlines()
        
        access_token = next(line for line in lines if line.startswith('ETSY_ACCESS_TOKEN=')).split('=')[1].strip()
        
        # Get listings
        listings_url = f'https://openapi.etsy.com/v3/application/shops/{shop_id}/listings'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': CLIENT_ID
        }

        data = {
            'state': 'draft'
        }
        
        response = requests.get(listings_url, headers=headers, params=data)
        response.raise_for_status()
        
        listings = response.json()
        
        return listings
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}

@app.get("/delete-listing")
def delete_listing():
    try:
        # Load access token from .env file
        with open('.env', 'r') as file:
            lines = file.readlines()
        
        access_token = next(line for line in lines if line.startswith('ETSY_ACCESS_TOKEN=')).split('=')[1].strip()

        delete_url = f'https://openapi.etsy.com/v3/application/listings/1871435245'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': CLIENT_ID
        }
        
        response = requests.delete(delete_url, headers=headers)
        response.raise_for_status()
        
        return {"message": "Listing deleted successfully!"}
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": e.response.text if hasattr(e, 'response') else None}




if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 