import { useState } from "react";
import axios from "axios";
import { auth } from "./firebase";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [amazonProducts, setAmazonProducts] = useState([]);
  const [snapdealProducts, setSnapdealProducts] = useState([]);
  const [cromaProducts, setCromaProducts] = useState([]);
  const [flipkartProducts, setFlipkartProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedSites, setSelectedSites] = useState({
    amazon: true,
    snapdeal: false,
    croma: false,
    flipkart: false
  });

  const handleLogout = async () => {
    try {
      await auth.signOut();
      navigate("/");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  // Helper function to convert price string to number for sorting
  const parsePriceToNumber = (priceStr) => {
    if (!priceStr) return Number.MAX_VALUE; // Handle undefined or empty prices
    // Remove currency symbol and convert to number
    const numericPrice = Number(priceStr.toString().replace(/[^\d.-]/g, ''));
    return isNaN(numericPrice) ? Number.MAX_VALUE : numericPrice;
  };

  // Sort products by price (lowest first)
  const sortProductsByPrice = (products) => {
    return [...products].sort((a, b) => {
      const priceA = parsePriceToNumber(a.price);
      const priceB = parsePriceToNumber(b.price);
      return priceA - priceB;
    });
  };

  // Handle site selection toggle
  const handleSiteToggle = (site) => {
    setSelectedSites(prev => ({
      ...prev,
      [site]: !prev[site]
    }));
  };

  // Check if at least one site is selected
  const isSiteSelected = Object.values(selectedSites).some(value => value);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery || !isSiteSelected) return;

    setIsLoading(true);
    try {
      // Create site selection parameter
      const selectedSitesParam = Object.entries(selectedSites)
        .filter(([_, isSelected]) => isSelected)
        .map(([site, _]) => {
          switch(site) {
            case 'amazon': return '1';
            case 'snapdeal': return '2';
            case 'croma': return '3';
            case 'flipkart': return '4';
            default: return '';
          }
        })
        .join(',');

      const response = await axios.get(
        `http://127.0.0.1:8000/search?query=${searchQuery}&sites=${selectedSitesParam}`
      );
      
      // Sort products by price (lowest first) before setting state
      setAmazonProducts(sortProductsByPrice(response.data.amazon_products || []));
      setSnapdealProducts(sortProductsByPrice(response.data.snapdeal_products || []));
      setCromaProducts(sortProductsByPrice(response.data.croma_products || []));
      setFlipkartProducts(sortProductsByPrice(response.data.flipkart_products || []));
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col p-4 md:p-6 lg:p-8">
      {/* Header */}
      <header className="w-full flex justify-between items-center mb-8 p-4 bg-gray-800 rounded-lg shadow-lg">
        <div className="flex items-center">
          <div className="h-10 w-10 rounded-full flex items-center justify-center mr-3">
          <img className="mt-1 flex items-center justify-center" src="/logo1.png" alt="logo" width="80" height="80" />
          </div>
          <div>
            <h1 className="font-bold text-xl text-white main-name">VALEUR</h1>
            <p className="text-gray-400 text-sm">
              Welcome, {auth.currentUser?.displayName || auth.currentUser?.email}
            </p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="bg-gray-700 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors duration-200 flex items-center"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
          </svg>
          Logout
        </button>
      </header>

      {/* Search Form */}
      <div className="w-full max-w-3xl mx-auto mb-8">
        <form onSubmit={handleSearch} className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="Enter product name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 text-white bg-gray-800 border border-gray-700 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          />
          
          {/* Site Selection */}
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-semibold mb-3 text-gray-400">Select required sites:</h3>
            <div className="flex flex-wrap gap-3">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedSites.amazon}
                  onChange={() => handleSiteToggle('amazon')}
                  className="sr-only"
                />
                <div className={`px-3 py-2 rounded-full flex items-center ${selectedSites.amazon ? 'bg-blue-800 text-white' : 'bg-gray-700 text-gray-300'}`}>
                  <span className="text-sm">Amazon</span>
                </div>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedSites.snapdeal}
                  onChange={() => handleSiteToggle('snapdeal')}
                  className="sr-only"
                />
                <div className={`px-3 py-2 rounded-full flex items-center ${selectedSites.snapdeal ? 'bg-red-700 text-white' : 'bg-gray-700 text-gray-300'}`}>
                  <span className="text-sm">Snapdeal</span>
                </div>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedSites.croma}
                  onChange={() => handleSiteToggle('croma')}
                  className="sr-only"
                />
                <div className={`px-3 py-2 rounded-full flex items-center ${selectedSites.croma ? 'bg-green-700 text-white' : 'bg-gray-700 text-gray-300'}`}>
                  <span className="text-sm">Croma</span>
                </div>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedSites.flipkart}
                  onChange={() => handleSiteToggle('flipkart')}
                  className="sr-only"
                />
                <div className={`px-3 py-2 rounded-full flex items-center ${selectedSites.flipkart ? 'bg-yellow-600 text-white' : 'bg-gray-700 text-gray-300'}`}>
                  <span className="text-sm">Flipkart</span>
                </div>
              </label>
            </div>
            {!isSiteSelected && (
              <p className="text-red-500 text-sm mt-2">Please select at least one site</p>
            )}
          </div>
          
          <button
            type="submit"
            disabled={isLoading || !isSiteSelected}
            className={`bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center md:w-full ${(!isSiteSelected || isLoading) ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isLoading ? (
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            )}
            Search
          </button>
        </form>
      </div>

      {/* Results Section */}
      <div className=" grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full">
        {/* Amazon Results - Only show if selected */}
        {selectedSites.amazon && (
          <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
            <div className="flex items-center mb-4">
              <img className="mt-1" src="/amazon.png" alt="Amazon" width="100" height="100" />
            </div>
            
            {amazonProducts.length > 0 ? (
              <ul className="space-y-4">
                {amazonProducts.map((product, index) => (
                  <li key={index} className="bg-gray-900 rounded-lg p-4 transition-transform hover:scale-102 hover:shadow-xl">
                    <div className="flex flex-col">
                      <div className="flex justify-center mb-3">
                        {product.image_url && product.image_url !== "No Image" ? (
                          <img
                            src={product.image_url}
                            alt={product.title}
                            className="w-32 h-32 object-contain rounded bg-white p-2"
                          />
                        ) : (
                          <div className="w-32 h-32 bg-gray-700 rounded flex items-center justify-center">
                            <span className="text-gray-500">No Image</span>
                          </div>
                        )}
                      </div>
                      <h3 className="text-md font-bold line-clamp-2 mb-2">{product.title}</h3>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-lg font-bold text-green-400">{product.price}</span>
                        {product.rating && (
                          <span className="bg-yellow-600 text-white text-xs px-2 py-1 rounded-full flex items-center">
                            <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                            </svg>
                            {product.rating}
                          </span>
                        )}
                      </div>
                      <a
                        href={`https://www.amazon.in/dp/${product.asin}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-blue-600 hover:bg-blue-700 text-white text-center py-2 rounded-md mt-2 transition-colors"
                      >
                        View Product
                      </a>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p>No Amazon products found</p>
              </div>
            )}
          </div>
        )}

        {/* Snapdeal Results - Only show if selected */}
        {selectedSites.snapdeal && (
          <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
            <div className="flex items-center mb-4">
              <img src="/snap.png" alt="Snapdeal" width="120" height="120" />
            </div>
            
            {snapdealProducts.length > 0 ? (
              <ul className="space-y-4">
                {snapdealProducts.map((product, index) => {
                  const snapdealUrl = product.product_url.replace(
                    /^https:\/\/www\.snapdeal\.comhttps:\/\/www\.snapdeal\.com/,
                    "https://www.snapdeal.com"
                  );

                  return (
                    <li key={index} className="bg-gray-900 rounded-lg p-4 transition-transform hover:scale-102 hover:shadow-xl">
                      <div className="flex flex-col">
                        <div className="flex justify-center mb-3">
                          {product.image_url && product.image_url !== "No Image" ? (
                            <img
                              src={product.image_url}
                              alt={product.title}
                              className="w-32 h-32 object-contain rounded bg-white p-2"
                            />
                          ) : (
                            <div className="w-32 h-32 bg-gray-700 rounded flex items-center justify-center">
                              <span className="text-gray-500">No Image</span>
                            </div>
                          )}
                        </div>
                        <h3 className="text-md font-bold line-clamp-2 mb-2">{product.title}</h3>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-lg font-bold text-green-400">₹{product.price}</span>
                          {product.rating && (
                            <span className="bg-yellow-600 text-white text-xs px-2 py-1 rounded-full flex items-center">
                              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                              </svg>
                              {product.rating}
                            </span>
                          )}
                        </div>
                        {product.product_url && (
                          <a
                            href={snapdealUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-red-600 hover:bg-red-700 text-white text-center py-2 rounded-md mt-2 transition-colors"
                          >
                            View Product
                          </a>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p>No Snapdeal products found</p>
              </div>
            )}
          </div>
        )}

        {/* Croma Results - Only show if selected */}
        {selectedSites.croma && (
          <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
            <div className="flex items-center mb-4">
              <img src="/croma.png" alt="Croma" width="100" height="100" />
            </div>
            
            {cromaProducts.length > 0 ? (
              <ul className="space-y-4">
                {cromaProducts.map((product, index) => (
                  <li key={index} className="bg-gray-900 rounded-lg p-4 transition-transform hover:scale-102 hover:shadow-xl">
                    <div className="flex flex-col">
                      <div className="flex justify-center mb-3">
                        {product.image_url && product.image_url !== "No Image" ? (
                          <img
                            src={product.image_url}
                            alt={product.title}
                            className="w-32 h-32 object-contain rounded bg-white p-2"
                          />
                        ) : (
                          <div className="w-32 h-32 bg-gray-700 rounded flex items-center justify-center">
                            <span className="text-gray-500">No Image</span>
                          </div>
                        )}
                      </div>
                      <h3 className="text-md font-bold line-clamp-2 mb-2">{product.title || "No Title"}</h3>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-lg font-bold text-green-400">₹{product.price || "N/A"}</span>
                        {product.original_price && (
                          <span className="line-through text-gray-400 text-sm ml-2">
                            ₹{product.original_price}
                          </span>
                        )}
                        {product.discount && (
                          <span className="bg-yellow-600 text-white text-xs px-2 py-1 rounded-full ml-2">
                            {product.discount}
                          </span>
                        )}
                      </div>
                      {product.product_url && (
                        <a
                          href={product.product_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="bg-green-600 hover:bg-green-700 text-white text-center py-2 rounded-md mt-2 transition-colors"
                        >
                          View Product
                        </a>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p>No Croma products found</p>
              </div>
            )}
          </div>
        )}

        {/* Flipkart Results - Only show if selected */}
        {selectedSites.flipkart && (
          <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
            <div className="flex items-center mb-4">
              <img src="/flip.png" alt="Flipkart" width="130" height="130" />
            </div>
            
            {flipkartProducts.length > 0 ? (
              <ul className="space-y-4">
                {flipkartProducts.map((product, index) => (
                  <li key={index} className="bg-gray-900 rounded-lg p-4 transition-transform hover:scale-102 hover:shadow-xl">
                    <div className="flex flex-col">
                      <div className="flex justify-center mb-3">
                        {product.image_url && product.image_url !== "No Image" ? (
                          <img
                            src={product.image_url}
                            alt={product.title}
                            className="w-32 h-32 object-contain rounded bg-white p-2"
                          />
                        ) : (
                          <div className="w-32 h-32 bg-gray-700 rounded flex items-center justify-center">
                            <span className="text-gray-500">No Image</span>
                          </div>
                        )}
                      </div>
                      <h3 className="text-md font-bold line-clamp-2 mb-2">{product.title || "No Title"}</h3>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-lg font-bold text-green-400">₹{product.price || "N/A"}</span>
                        {product.discount && (
                          <span className="bg-yellow-600 text-white text-xs px-2 py-1 rounded-full">
                            {product.discount}
                          </span>
                        )}
                      </div>
                      {product.product_url && (
                        <a
                          href={product.product_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="bg-yellow-600 hover:bg-yellow-700 text-white text-center py-2 rounded-md mt-2 transition-colors"
                        >
                          View Product
                        </a>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p>No Flipkart products found</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-gray-500 text-sm">
        <p>© {new Date().getFullYear()} Price Comparison | All rights reserved</p>
      </footer>
    </div>
  );
};

export default Home;