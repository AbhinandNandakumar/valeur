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

  const handleLogout = async () => {
    try {
      await auth.signOut();
      navigate("/");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const handleSearch = async (e) => {
    console.log("hi");
    e.preventDefault();
    if (!searchQuery) return;

    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/search?query=${searchQuery}`
      );
      setAmazonProducts(response.data.amazon_products);
      setSnapdealProducts(response.data.snapdeal_products);
      setCromaProducts(response.data.croma_products);
      setFlipkartProducts(response.data.flipkart_products);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center justify-center p-8">
      {/* Top Bar */}
      <div className="absolute top-4 left-4 text-lg font-semibold">
        Welcome, {auth.currentUser?.displayName || auth.currentUser?.email}
      </div>

      <button
        onClick={handleLogout}
        className="absolute top-4 right-4 bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors"
      >
        Logout
      </button>

      <form onSubmit={handleSearch} className="w-full max-w-md flex">
        <input
          type="text"
          placeholder="Enter product name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 text-white bg-gray-800 border border-white rounded-l-lg outline-none"
        />
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-r-lg"
        >
          Search
        </button>
      </form>

      {/* Display Results Side by Side */}
      <div className="mt-8 grid grid-cols-4 gap-8 w-full max-w-7xl">
        {/* Amazon Results */}
        <div>
          <h2 className="text-xl font-bold text-blue-400 mb-4">Amazon Results</h2>
          {console.log(amazonProducts)}
          {amazonProducts.length > 0 ? (
            
            <ul className="space-y-4">
              {amazonProducts.map((product, index) => (
                <li key={index} className="p-4 bg-gray-800 rounded-lg shadow">
                  {product.image_url && product.image_url !== "No Image" && (
                    <img
                      src={product.image_url}
                      alt={product.title}
                      className="w-32 h-32 object-cover mt-2 rounded"
                    />
                  )}
                  <h2 className="text-lg font-bold">{product.title}</h2>
                  {console.log(product.image_url)}
                  <p>Price: {product.price}</p>
                  <p>Rating: {product.rating}</p>
                  <a
                    href={`https://www.amazon.in/dp/${product.asin}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 block"
                  >
                    View on Amazon
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400">No Amazon products found</p>
          )}
        </div>

        {/* Snapdeal Results */}
        <div>
          <h2 className="text-xl font-bold text-red-400 mb-4">Snapdeal Results</h2>
          {snapdealProducts.length > 0 ? (
            <ul className="space-y-4">
              {snapdealProducts.map((product, index) => {
                const snapdealUrl = product.product_url.replace(
                  /^https:\/\/www\.snapdeal\.comhttps:\/\/www\.snapdeal\.com/,
                  "https://www.snapdeal.com"
                );

                return (
                  <li key={index} className="p-4 bg-gray-800 rounded-lg shadow">
                    {product.image_url && product.image_url !== "No Image" && (
                    <img
                      src={product.image_url}
                      alt={product.title}
                      className="w-32 h-32 object-cover mt-2 rounded"
                    />
                  )}
                    <h2 className="text-lg font-bold">{product.title}</h2>
                    <p>Price: {product.price}</p>
                    <p>Rating: {product.rating}</p>
                    {product.product_url && (
                      <a
                        href={snapdealUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-red-400 block"
                      >
                        View on Snapdeal
                      </a>
                    )}
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="text-gray-400">No Snapdeal products found</p>
          )}
        </div>

        {/* Chroma Results */}
        {/* Croma Results */}
        <div>
          <h2 className="text-xl font-bold text-green-400 mb-4">
            Croma Results
          </h2>
          {cromaProducts.length > 0 ? (
            <ul className="space-y-4">
              {cromaProducts.map((product, index) => (
                <li key={index} className="p-4 bg-gray-800 rounded-lg shadow">
                  <h2 className="text-lg font-bold">
                    {product.title || "No Title"}
                  </h2>
                  <p>Price: ₹{product.price || "N/A"}</p>
                  {product.original_price && (
                    <p className="line-through text-gray-400">
                      Original: ₹{product.original_price}
                    </p>
                  )}
                  {product.discount && (
                    <p className="text-yellow-400">
                      Discount: {product.discount}
                    </p>
                  )}
                  {product.image_url && product.image_url !== "No Image" && (
                    <img
                      src={product.image_url}
                      alt={product.title}
                      className="w-32 h-32 object-cover mt-2 rounded"
                    />
                  )}
                  {product.product_url && (
                    <a
                      href={product.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-green-400 block mt-2"
                    >
                      View on Croma
                    </a>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400">No Croma products found</p>
          )}
        </div>

        {/* Flipkart Results */}
        <div>
          <h2 className="text-xl font-bold text-purple-400 mb-4">
            Flipkart Results
          </h2>
          {flipkartProducts.length > 0 ? (
            <ul className="space-y-4">
              {flipkartProducts.map((product, index) => (
                <li key={index} className="p-4 bg-gray-800 rounded-lg shadow">
                  <h2 className="text-lg font-bold">
                    {product.title || "No Title"}
                  </h2>
                  <p>Price: ₹{product.price || "N/A"}</p>
                  {product.discount && (
                    <p className="text-yellow-400">
                      Discount: {product.discount}
                    </p>
                  )}
                  {product.image_url && product.image_url !== "No Image" && (
                    <img
                      src={product.image_url}
                      alt={product.title}
                      className="w-32 h-32 object-cover mt-2 rounded"
                    />
                  )}
                  {product.product_url && (
                    <a
                      href={product.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-400 block mt-2"
                    >
                      View on Flipkart
                    </a>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400">No Flipkart products found</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;