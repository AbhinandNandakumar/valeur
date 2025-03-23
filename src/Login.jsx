import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth, provider, signInWithPopup, signInWithEmailAndPassword, sendEmailVerification } from './firebase';
import google from './images/google.png';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      if (!user.emailVerified) {
        setError('Please verify your email before logging in. Check your inbox for the verification email.');
        await auth.signOut();  // Force logout if not verified
        return;
      }

      alert(`Welcome back, ${user.email}`);
      navigate("/home");
      
    } catch (error) {
      if (error.code === 'auth/user-not-found') {
        setError('No account found with this email.');
      } else if (error.code === 'auth/wrong-password') {
        setError('Incorrect password.');
      } else {
        setError('Error logging in. Please try again.');
      }
      console.error('Login error:', error);
    }
  };
  
  const handleResendVerificationEmail = async () => {
    try {
      const user = auth.currentUser;
      if (user) {
        await sendEmailVerification(user);
        alert('Verification email sent again. Please check your inbox.');
      }
    } catch (error) {
      console.error('Error sending verification email:', error);
      alert('Error sending verification email. Please try again later.');
    }
  };
  
  const handleGoogleLogin = async () => {
    try {
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      console.log('Google Login:', user);
      navigate("/home");
    } catch (error) {
      setError('Error signing in with Google.');
      console.error('Google sign-in error:', error);
    }
  };

  return (
    <div className="fixed inset-0 flex justify-center items-center bg-black bg-opacity-70">
      <div className="bg-gray-900 p-8 rounded-lg shadow-2xl w-full max-w-md border border-gray-700 backdrop-blur-sm">
        <div className="mb-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-2">Welcome Back</h2>
          <p className="text-gray-400">Sign in to continue to your account</p>
        </div>

        {/* Email/Password Login Form */}
        <form onSubmit={handleEmailLogin} className="space-y-5 mb-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-1">Email</label>
            <div className="relative">
              <input
                id="email"
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-100 placeholder-gray-500"
                required
              />
            </div>
          </div>
          
          <div>
            <div className="flex items-center justify-between mb-1">
              <label htmlFor="password" className="block text-sm font-medium text-gray-300">Password</label>
              <a href="#" className="text-sm text-blue-400 hover:text-blue-300">Forgot password?</a>
            </div>
            <div className="relative">
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-100 placeholder-gray-500"
                required
              />
            </div>
          </div>
          
          {error && (
            <div className="p-3 bg-red-900 bg-opacity-30 border border-red-800 rounded-md">
              <p className="text-red-300 text-sm">{error}</p>
              {error === 'Please verify your email before logging in. Check your inbox for the verification email.' && (
                <button
                  type="button"
                  onClick={handleResendVerificationEmail}
                  className="text-blue-400 hover:text-blue-300 mt-1 text-sm font-medium"
                >
                  Resend Verification Email
                </button>
              )}
            </div>
          )}
          
          <button 
            type="submit" 
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium shadow-md"
          >
            Sign In
          </button>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-700"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-gray-900 text-gray-400">Or continue with</span>
          </div>
        </div>

        {/* Google Sign In */}
        <button 
          onClick={handleGoogleLogin} 
          className="w-full flex items-center justify-center border border-gray-700 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors duration-200 bg-gray-800"
        >
          <img src={google} alt="Google" className="w-5 h-5 mr-3" />
          <span className="text-white font-medium">Sign in with Google</span>
        </button>
        
        <p className="mt-6 text-center text-gray-400 text-sm">
          Don't have an account? <a href="#" className="text-blue-400 hover:text-blue-300 font-medium">Create account</a>
        </p>
      </div>
    </div>
  );
};

export default Login;