import { 
  initializeApp 
} from 'firebase/app';

import { 
  getAuth, 
  GoogleAuthProvider, 
  signInWithPopup,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  sendEmailVerification
} from 'firebase/auth';

const firebaseConfig = {
    apiKey: "AIzaSyBw7qbcH7XpBE4C9r0jo18tSgS4EgVNDOQ",
    authDomain: "valeur-ec93b.firebaseapp.com",
    projectId: "valeur-ec93b",
    storageBucket: "valeur-ec93b.firebasestorage.app",
    messagingSenderId: "10573819023",
    appId: "1:10573819023:web:8f5884a3e49b284b4fd4fa",
    measurementId: "G-2L7LJL08QG"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export { 
    auth, 
    provider, 
    signInWithPopup,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    sendEmailVerification
};
