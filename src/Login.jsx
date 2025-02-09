import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth, provider, signInWithPopup, signInWithEmailAndPassword,sendEmailVerification } from './firebase';
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
    <div className="fixed inset-0 flex justify-center items-center bg-black bg-opacity-50">
      <div className="bg-gray-800 p-6 rounded-lg shadow-xl w-full max-w-md border border-gray-700">
        <h2 className="text-2xl font-bold text-center text-gray-100 mb-4">Login</h2>

        {/* Email/Password Login Form */}
        <form onSubmit={handleEmailLogin} className="mb-6">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full mb-3 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:ring-blue-500 text-gray-100"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full mb-3 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:ring-blue-500 text-gray-100"
            required
          />
          {error === 'Please verify your email before logging in. Check your inbox for the verification email.' && (
  <button
    onClick={handleResendVerificationEmail}
    className="text-blue-400 hover:underline mt-2 text-sm"
  >
    Resend Verification Email
  </button>
)}

          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button type="submit" className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">
            Login
          </button>
        </form>

        {/* Google Sign In */}
        <button onClick={handleGoogleLogin} className="w-full flex items-center justify-center border border-gray-600 py-2 px-4 rounded-md hover:bg-gray-700 bg-white">
          <img src={google} alt="Google" className="w-5 h-5 mr-2" />
          Sign in with Google
        </button>

      </div>
    </div>
  );
};

export default Login;
