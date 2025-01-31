import requests
from typing import Dict, Any, Optional

def search_book_by_title_openlibrary(book_title: str) -> Dict[str, Any]:
    """
    Fetch book metadata from Open Library API with improved error handling
    """
    BASE_URL = "https://openlibrary.org/search.json"
    
    try:
        title = book_title.split(':')[0].strip()  # Take only the part before ':' and remove whitespace
        response = requests.get(BASE_URL, params={'title': title, 'limit': 1})
        response.raise_for_status()
        
        data = response.json()
        if not data.get('docs'):
            return {"status": "error", "message": "No book found"}
            
        book = data['docs'][0]
        
        # Build book details
        book_details = {
            'status': 'success',
            'data': {
                'title': book.get('title', 'N/A'),
                'authors': book.get('author_name', ['Unknown']),
                'publish_year': book.get('first_publish_year', 'N/A'),
                'publishers': book.get('publisher', ['N/A']),
                'isbn_10': None,
                'isbn_13': None,
                'language': book.get('language', ['N/A']),
                'number_of_pages': book.get('number_of_pages_median', 'N/A'),
                'subjects': book.get('subject', []),
            }
        }
        
        # Extract ISBNs if available
        if 'isbn' in book:
            book_details['data']['isbn_10'] = next((isbn for isbn in book['isbn'] if len(isbn) == 10), None)
            book_details['data']['isbn_13'] = next((isbn for isbn in book['isbn'] if len(isbn) == 13), None)
        
        # Get cover image if available
        if 'cover_i' in book:
            book_details['data']['cover_image'] = f"https://covers.openlibrary.org/b/id/{book['cover_i']}-L.jpg"
        
        return book_details
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"API request failed: {str(e)}"
        }
    except (KeyError, ValueError) as e:
        return {
            "status": "error",
            "message": f"Data parsing error: {str(e)}"
        }