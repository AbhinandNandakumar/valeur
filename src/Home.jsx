import { useState } from 'react';
import axios from 'axios';
import { auth } from './firebase';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);

  const handleLogout = async () => {
    try {
      await auth.signOut();
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };


  const handleSearch = async (e) => {
    e.preventDefault();

    if (!searchQuery) return;

    try {
      const response = await axios.get(`http://127.0.0.1:8000/search?query=${searchQuery}`);
      setProducts(response.data.products);
    } catch (error) {
      console.error('Error fetching data:', error);
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
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-r-lg">
          Search
        </button>
      </form>

      {/* Display Results */}
      <div className="mt-8 w-full max-w-3xl">
        {products.length > 0 ? (
          <ul className="space-y-4">
            {products.map((product, index) => (
              <li key={index} className="p-4 bg-gray-800 rounded-lg shadow">
                <h2 className="text-lg font-bold">{product.title}</h2>
                <p>Price: {product.price}</p>
                <p>Rating: {product.rating}</p>
                <a href={`https://www.amazon.in/dp/${product.asin}`} target="_blank" rel="noopener noreferrer" className="text-blue-400">
                  View on Amazon
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-400">No products found</p>
        )}
      </div>
    </div>
  );
};

export default Home;
