import requests
from bs4 import BeautifulSoup
import re
import random

def download_pdf(book_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': book_url
    }

    with requests.Session() as session:
        # Fetch the book page
        response = session.get(book_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.find('h1').text.strip()

        # Extract ID and Session from the button's data-preview attribute
        button = soup.find('button', {'id': 'previewButtonMain'})
        if not button:
            return None

        data_preview = button.get('data-preview', '')
        if not data_preview:
            return None

        # Parse ID and Session from the URL in data-preview
        params = {}
        parts = data_preview.split('?')[1].split('&')
        for part in parts:
            key, value = part.split('=')
            params[key] = value


        # Extract the "r" parameter (random token) from JavaScript logic
        # Example: Look for a script containing "downloadButton"
        r_value = None
        # Generate random r value between 100-999
        r_value = str(random.randint(100, 999))

        if not r_value:
            return None

        # Step 2: Fetch the intermediate "/ebook/broken" page
        broken_url = (
            f"https://www.pdfdrive.com/ebook/broken?"
            f"id={params['id']}&session={params['session']}&r={r_value}"
        )
        broken_response = session.get(broken_url, headers=headers)
        broken_soup = BeautifulSoup(broken_response.text, 'html.parser')

        # Step 3: Extract the final PDF URL from the download button
        download_link = broken_soup.find('a', {'class': 'btn-user'})
        print("I am here: ", download_link)
        if not download_link:
            return None


        pdf_path = download_link.get('href')
        pdf_url = f"https://www.pdfdrive.com{pdf_path}"


        # Step 4: Download the actual PDF
        pdf_response = session.get(
            pdf_url,
            headers=headers,
            stream=True
        )

        if pdf_response.headers.get('Content-Type') == 'application/pdf':
            filename = f"{title.replace(' ', '_')}.pdf"
            with open(filename, 'wb') as f:
                for chunk in pdf_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        else:
            return None

def extract_title(book_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': book_url
    }
    
    with requests.Session() as session:
        # Fetch the book page
        response = session.get(book_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.find('h1').text.strip()
        return title
    