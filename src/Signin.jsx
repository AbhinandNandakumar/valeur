import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; 
import { 
  auth, 
  provider, 
  signInWithPopup,
  createUserWithEmailAndPassword ,
  sendEmailVerification
} from './firebase';
import google from './images/google.png';

const SignIn = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleEmailSignUp = async (e) => {
    e.preventDefault();
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Send verification email
      await sendEmailVerification(user);
  
      console.log('New User Created:', user);
      alert(`Account created successfully! A verification email has been sent to ${user.email}. Please verify your email before logging in.`);
      setEmail('');
    setPassword('');
    setError('');
      
    } catch (error) {
      if (error.code === 'auth/email-already-in-use') {
        setError('An account with this email already exists.');
      } else if (error.code === 'auth/weak-password') {
        setError('Password should be at least 6 characters long.');
      } else if (error.code === 'auth/invalid-email') {
        setError('Please enter a valid email address.');
      } else {
        setError('Error creating account. Please try again.');
      }
      console.error('Error during sign-up:', error);
    }
  };
  
  const handleGoogleSignIn = async () => {
    try {
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      console.log('User:', user);
      alert(`Welcome ${user.displayName}`);
    } catch (error) {
      setError('Error signing in with Google. Please try again.');
      console.error('Error during Google sign-in:', error);
    }
  };

  return (
    <div className="flex flex-col justify-center items-center min-h-screen p-4 relative">
      
      {/* Login Button (Top Right Corner) */}
      <button 
        onClick={() => navigate('/login')} 
        className="absolute top-4 right-4 bg-gray-700 text-white px-4 py-2 rounded-md hover:bg-gray-600 transition"
      >
        Login
      </button>

      <div className="bg-gray-800 p-8 rounded-lg shadow-xl w-full max-w-md border border-gray-700">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-100">Create Account</h2>
        
        {/* Email/Password Sign Up Form */}
        <form onSubmit={handleEmailSignUp} className="mb-6">
          <div className="mb-4">
            <label htmlFor="email" className="block text-gray-300 text-sm font-medium mb-2">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-100 placeholder-gray-400"
              required
              placeholder="Enter your email"
            />
          </div>
          
          <div className="mb-6">
            <label htmlFor="password" className="block text-gray-300 text-sm font-medium mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-100 placeholder-gray-400"
              required
              placeholder="Choose a password (min. 6 characters)"
              minLength="6"
            />
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-900/50 text-red-200 text-sm text-center rounded-md border border-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
          >
            Create Account
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-700"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-gray-800 text-gray-400">Or continue with</span>
          </div>
        </div>

        {/* Google Sign In Button */}
        <button
          onClick={handleGoogleSignIn}
          className="w-full border border-gray-600 text-gray-300 py-2 px-4 rounded-md hover:bg-gray-700 transition-colors flex items-center justify-center"
        >
          <img src={google} alt="Google icon" className="w-5 h-5 mr-3" />
          <span>Sign in with Google</span>
        </button>
      </div>
    </div>
  );
};

export default SignIn;
