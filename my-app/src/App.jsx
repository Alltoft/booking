import React, { useState, useEffect } from 'react';
// Add RefreshCw to imports
import { BookOpen, Upload, ShoppingBag, Loader2, RefreshCw } from 'lucide-react';
import { api } from './api';
import toast from 'react-hot-toast';

function App() {
  // Add new state for token status
  const [hasToken, setHasToken] = useState(false);
  const [tokenLoading, setTokenLoading] = useState(false);
  
  // Add existing states
  const [pdfUrl, setPdfUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [bookData, setBookData] = useState(null);

  // Add useEffect to check token status on mount
  useEffect(() => {
    checkToken();
  }, []);

  // Add function to check token
  const checkToken = async () => {
    try {
      const response = await api.getUser();
      setHasToken(!response.error);
    } catch (error) {
      setHasToken(false);
    }
  };

  // Add function to handle token operations
  const handleToken = async () => {
    if (hasToken) {
      setTokenLoading(true);
      try {
        const response = await api.refreshToken();
        if (response.error) throw new Error(response.error);
        toast.success('Token refreshed successfully!');
      } catch (error) {
        toast.error(error.message || 'Failed to refresh token');
      } finally {
        setTokenLoading(false);
      }
    } else {
      window.open('http://localhost:8000/', '_blank');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!pdfUrl) return;

    setLoading(true);
    try {
      // Step 1: Get PDF and extract info
      console.log('downloadeding pdf...');
      const pdfResponse = await api.getBookPdf(pdfUrl);
      if (pdfResponse.error) throw new Error(pdfResponse.error);
      console.log(pdfResponse);

      // Step 2: Search book details
      console.log('searching book details...');
      const bookDetails = await api.searchBook(pdfResponse.title);
      setBookData(bookDetails);
      
      // Step 3: Generate description
      console.log('generating description...');
      console.log(bookDetails);
      const descriptionData = await api.generateDescription(bookDetails);
      
      // Step 4: Get user/shop info
      console.log('getting user info...');
      const userData = await api.getUser();
      
      console.log('creating listing...');
      // Step 5: Create listing
      const listingData = await api.createListing(
        userData.shop_id,
        pdfResponse.title,
        descriptionData.description
      );

      // Step 6: Upload cover image
      // wait for 1sec to avoid rate limiting before uploading image
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      console.log('uploading cover image...');
      if (bookDetails.cover_image) {
        await api.uploadListingImage(
          userData.shop_id,
          listingData.listing_id,
          bookDetails.cover_image
        );
      }

      // wait for 1sec to avoid rate limiting before uploading file
      console.log('uploading pdf file...');
      console.log(userData.shop_id, listingData, pdfResponse);
      await new Promise((resolve) => setTimeout(resolve, 1000));
      // Step 7: Upload PDF file
      await api.uploadListingFile(
        userData.shop_id,
        listingData.listing_id,
        pdfResponse.pdf
      );

      // Step 8: Clean up downloaded PDF
      console.log('deleting pdf...');
      await api.deletePdf(pdfResponse.pdf);

      toast.success('Listing created successfully!');
      setStep(1);
      setPdfUrl('');
      setBookData(null);
    } catch (error) {
      toast.error(error.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  // Modify header section in return statement
  return (
    <div className="min-h-screen bg-[#FAF9F8]">
      <header className="bg-white border-b border-[#E1E3DF] py-4">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShoppingBag className="w-8 h-8 text-[#F1641E]" />
              <h1 className="text-2xl font-bold text-[#222222]">
                Etsy Listing Automation
              </h1>
            </div>
            <button
              onClick={handleToken}
              disabled={tokenLoading}
              className="inline-flex items-center gap-2 px-4 py-2 bg-[#F1641E] text-white rounded-lg hover:bg-[#E44D1D] focus:outline-none focus:ring-2 focus:ring-[#F1641E] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {tokenLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing...
                </>
              ) : hasToken ? (
                <>
                  <RefreshCw className="w-4 h-4" />
                  Refresh Token
                </>
              ) : (
                <>
                  <ShoppingBag className="w-4 h-4" />
                  Get Access Token
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-[#E1E3DF]">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  step >= 1 ? 'bg-[#F1641E] text-white' : 'bg-[#E1E3DF] text-[#595959]'
                }`}>
                  1
                </div>
                <span className="text-[#222222] font-medium">Enter PDF URL</span>
              </div>
              <div className="flex-1 h-px bg-[#E1E3DF]" />
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  step >= 2 ? 'bg-[#F1641E] text-white' : 'bg-[#E1E3DF] text-[#595959]'
                }`}>
                  2
                </div>
                <span className="text-[#222222] font-medium">Create Listing</span>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label 
                  htmlFor="pdfUrl" 
                  className="block text-sm font-medium text-[#222222] mb-2"
                >
                  PDF Drive URL
                </label>
                <div className="flex gap-2">
                  <div className="flex-1 relative">
                    <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#595959]" />
                    <input
                      type="url"
                      id="pdfUrl"
                      value={pdfUrl}
                      onChange={(e) => setPdfUrl(e.target.value)}
                      placeholder="https://www.pdfdrive.com/book-title.html"
                      className="w-full pl-10 pr-4 py-2 border border-[#E1E3DF] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#F1641E] focus:border-transparent"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="inline-flex items-center gap-2 px-6 py-2 bg-[#F1641E] text-white rounded-lg hover:bg-[#E44D1D] focus:outline-none focus:ring-2 focus:ring-[#F1641E] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5" />
                        Create Listing
                      </>
                    )}
                  </button>
                </div>
              </div>

              {bookData && (
                <div className="p-4 bg-[#FDEEE8] rounded-lg">
                  <h3 className="font-medium text-[#222222] mb-2">Book Details</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-[#595959]">Title</p>
                      <p className="text-[#222222]">{bookData.title}</p>
                    </div>
                    <div>
                      <p className="text-sm text-[#595959]">Author</p>
                      <p className="text-[#222222]">{bookData.authors?.join(', ')}</p>
                    </div>
                  </div>
                </div>
              )}
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;