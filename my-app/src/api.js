import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

export const api = {
  async getBookPdf(url) {
    const response = await axios.get(`${BASE_URL}/get-book-pdf`, {
      params: { book_url: url }
    });
    return response.data;
  },

  async searchBook(title) {
    const response = await axios.get(`${BASE_URL}/search-book`, {
      params: { title }
    });
    return response;
  },

  async generateDescription(book_details) {
    const response = await axios.get(`${BASE_URL}/generate-description`, {
        params: JSON.parse(JSON.stringify(book_details))  // Serialize nested objects properly
    });
    return response.data;
},

  async getUser() {
    const response = await axios.get(`${BASE_URL}/get-user`);
    return response.data;
  },

  async createListing(shopId, title, description) {
    const response = await axios.get(`${BASE_URL}/create-listing`, {
      params: { shop_id: shopId, title, description }
    });
    return response.data;
  },

  async uploadListingImage(shopId, listingId, imageUrl) {
    const response = await axios.get(`${BASE_URL}/upload-listing-image`, {
      params: { shop_id: shopId, listing_id: listingId, image_url: imageUrl }
    });
    return response.data;
  },

  async uploadListingFile(shopId, listingId, fileName) {
    const response = await axios.get(`${BASE_URL}/upload-listing-file`, {
      params: { shop_id: shopId, listing_id: listingId, file_name: fileName }
    });
    return response.data;
  },

  async deletePdf(fileName) {
    const response = await axios.get(`${BASE_URL}/delete-pdf`, {
      params: { file_name: fileName }
    });
    return response.data;
  },

  async refreshToken() {
    const response = await axios.get(`${BASE_URL}/refresh`);
    return response.data;
  }
};