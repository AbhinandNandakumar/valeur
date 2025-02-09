import { auth } from './firebase';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await auth.signOut();
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center text-gray-100">
      <h1 className="text-4xl font-bold mb-4">
        Welcome, {auth.currentUser?.displayName || auth.currentUser?.email}
      </h1>
      <button
        onClick={handleLogout}
        className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors"
      >
        Logout
      </button>
    </div>
  );
};

export default Home;