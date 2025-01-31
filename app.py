from flask import Flask, render_template, request, jsonify
from scraper import download_pdf, extract_title
from searchbook import search_book_by_title_openlibrary
# from prodomate import add_listing_sandbox
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process_book', methods=['POST'])
def process_book():
    try:
        # Get the PDFDrive URL from the form
        pdf_url = request.form.get('pdf_url')
        
        # First extract the title
        title = extract_title(pdf_url)
        if not title:
            return jsonify({'status': 'error', 'message': 'Failed to extract title'})
        
        # Download the PDF
        # filename = download_pdf(pdf_url)
        # if not filename:
        #     return jsonify({'status': 'error', 'message': 'Failed to download PDF'})
        
        # Get additional book metadata from OpenLibrary
        book_metadata = search_book_by_title_openlibrary(title)
        
        # Prepare Etsy listing data
        description = f"Digital PDF Book: {title}\n\n"
        if book_metadata['status'] == 'success':
            description += f"Author: {', '.join(book_metadata['data']['authors'])}\n"
            description += f"Published: {book_metadata['data']['publish_year']}\n"
            if book_metadata['data']['subjects']:
                description += f"\nSubjects: {', '.join(book_metadata['data']['subjects'][:5])}"
        
        # Create Etsy listing data
        etsy_data = {
            "status": "success",
            "message": "Book processed successfully!",
            "title": title[:140],  # Etsy title limit
            "description": description,
            "price": 9.99,  # Default price
            "quantity": 999,
            "materials": ["digital", "PDF", "ebook"],
            "tags": ["digital", "ebook", "PDF", "instant download", "digital download"],
            "filename": title,
            "book_details": book_metadata['data'] if book_metadata['status'] == 'success' else None
        }

        return jsonify(etsy_data)
        
        # etsy_result = add_listing_sandbox(**etsy_data)
        
        # if etsy_result.get('status') == 'success':
        #     return jsonify({
        #         'status': 'success',
        #         'message': 'Book processed and listed successfully!',
        #         'book_details': book_metadata['data'] if book_metadata['status'] == 'success' else None,
        #         'etsy_listing': etsy_result['data']
        #     })
        # else:
        #     return jsonify({
        #         'status': 'error',
        #         'message': f"Failed to create Etsy listing: {etsy_result.get('message')}"
        #     })
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 