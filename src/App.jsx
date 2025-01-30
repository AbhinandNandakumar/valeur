import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SignIn from './Signin';
import Login from './Login'; // Import Login component

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </Router>
  );
}

export default App;
