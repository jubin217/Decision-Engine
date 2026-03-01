import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
    apiKey: "AIzaSyCvmxoPYc9Rgs0PDv7lK7lzO8IkrxK_dw8",
    authDomain: "guardian-ai-ad48f.firebaseapp.com",
    projectId: "guardian-ai-ad48f",
    storageBucket: "guardian-ai-ad48f.firebasestorage.app",
    messagingSenderId: "603009116155",
    appId: "1:603009116155:web:f92925d4732ebd8e108d5e",
    measurementId: "G-T54G5MTNDH"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);
const db = getFirestore(app);

export { auth, db, analytics };
