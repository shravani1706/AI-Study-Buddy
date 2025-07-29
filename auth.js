import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
import { getFirestore, doc, setDoc, getDoc } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-firestore.js";

// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyCDUL22qqmCN4GNOVUATHE5PEvE85lPZQs",
    authDomain: "ai-study-buddy-da475.firebaseapp.com",
    projectId: "ai-study-buddy-da475",
    storageBucket: "ai-study-buddy-da475.firebasestorage.app",
    messagingSenderId: "815928406332",
    appId: "1:815928406332:web:ad14e3ad1eabb5f4626e39",
    measurementId: "G-E5EEP0VCMX"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth();
const db = getFirestore();
const provider = new GoogleAuthProvider();

// Handle Google Sign-In
document.getElementById("googleSignIn").addEventListener("click", () => {
    signInWithPopup(auth, provider)
        .then(async (result) => {
            const user = result.user;
            const userRef = doc(db, "users", user.uid);

            // Check if user exists in Firestore
            const userDoc = await getDoc(userRef);
            if (!userDoc.exists()) {
                // New user: Store data in Firestore
                await setDoc(userRef, {
                    name: user.displayName,
                    email: user.email,
                    streak: 0,
                    points: 0,
                    enrolledCourses: []
                });
            }

            // Save user session and redirect to features page
            localStorage.setItem("user", JSON.stringify({ uid: user.uid, name: user.displayName }));
            window.location.href = "features.html";
        })
        .catch((error) => console.error("Sign-in Error:", error));
});

// Check if user is already signed in
onAuthStateChanged(auth, (user) => {
    if (user) {
        window.location.href = "features.html"; // Redirect if already logged in
    }
});
