import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; 
import { 
  auth, 
  provider, 
  signInWithPopup,
  createUserWithEmailAndPassword,
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
    <div className="flex flex-col justify-center items-center min-h-screen bg-gray-900 p-4 relative">
      {/* Decorative graphics */}
      <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-r z-0"></div>
      <div className="absolute bottom-0 right-0 w-full h-32 bg-gradient-to-l z-0"></div>
      
      {/* Login Button (Top Right Corner) */}
      <button 
        onClick={() => navigate('/login')} 
        className="absolute top-4 right-4 bg-gray-800 text-gray-200 px-6 py-2 rounded-lg hover:bg-gray-700 transition-all shadow-lg border border-gray-700 z-10 flex items-center"
      >
        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
        </svg>
        Login
      </button>

      {/* Main content box with brand identity */}
      <div className="relative z-10 w-full max-w-md mt-3">
        <div className="mb-6 text-center">
        <div className="flex items-center justify-center mb-4">
        <img className="mt-1" src="/logo1.jpg" alt="logo" width="70" height="70" />
          <div className='flex flex-col items-start ml-5'>
          
          <h1  className='text-gray-400 font-bold text-3xl main-name'>VALEUR</h1>
          <h3  className='text-gray-400 tag-name '>Your Priceless Destination</h3>

          </div>
              

            </div>
        </div>
        
        <div className="bg-gray-800/90 backdrop-blur-sm p-8 rounded-xl shadow-2xl border border-gray-700">
          <h2 className="text-2xl font-bold mb-6 text-center text-gray-100">Create Account</h2>
          
          {/* Email/Password Sign Up Form */}
          <form onSubmit={handleEmailSignUp} className="mb-6 space-y-5">
            <div>
              <label htmlFor="email" className="block text-gray-300 text-sm font-medium mb-2">
                Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"></path>
                  </svg>
                </div>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 w-full px-4 py-3 bg-gray-700/70 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-100 placeholder-gray-400 transition-all"
                  required
                  placeholder="Enter your email"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="password" className="block text-gray-300 text-sm font-medium mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                  </svg>
                </div>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 w-full px-4 py-3 bg-gray-700/70 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-100 placeholder-gray-400 transition-all"
                  required
                  placeholder="Choose a password (min. 6 characters)"
                  minLength="6"
                />
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-900/40 text-red-200 text-sm rounded-lg border border-red-800 flex items-center">
                <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"></path>
                </svg>
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-4 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all font-medium shadow-lg transform hover:-translate-y-0.5"
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
              <span className="px-3 bg-gray-800 text-gray-400">Or continue with</span>
            </div>
          </div>

          {/* Google Sign In Button */}
          <button
            onClick={handleGoogleSignIn}
            className="w-full bg-gray-700 border border-gray-600 text-gray-200 py-3 px-4 rounded-lg hover:bg-gray-600 transition-all flex items-center justify-center shadow-lg"
          >
            <img src={google} alt="Google icon" className="w-5 h-5 mr-3" />
            <span>Sign in with Google</span>
          </button>
          
          {/* Additional help text */}
          <p className="mt-6 text-center text-gray-500 text-sm">
            By creating an account, you agree to our 
            <a href="#" className="text-blue-400 hover:text-blue-300 ml-1">Terms of Service</a> and 
            <a href="#" className="text-blue-400 hover:text-blue-300 ml-1">Privacy Policy</a>
          </p>
        </div>
      </div>
      
      {/* Footer */}
      <div className="mt-8 text-gray-500 text-sm text-center z-10">
        © {new Date().getFullYear()} Price Comparison. All rights reserved.
      </div>
    </div>
  );
};

export default SignIn;