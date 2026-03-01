import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from './firebase'
import Navbar from './components/Navbar'
import Dashboard from './components/Dashboard'
import Profile from './components/Profile'
import Statistics from './components/Statistics'
import Auth from './components/Auth'
import './components/Components.css'
import './App.css'

function App() {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (user) => {
            setUser(user)
            setLoading(false)
        })
        return () => unsubscribe()
    }, [])

    if (loading) {
        return (
            <div className="loading-screen">
                <div className="loader"></div>
            </div>
        )
    }

    return (
        <Router>
            <div className="app-container">
                {user && <Navbar user={user} />}
                <main className={user ? 'main-content' : 'auth-content'}>
                    <Routes>
                        <Route path="/auth" element={!user ? <Auth /> : <Navigate to="/" />} />
                        <Route path="/" element={user ? <Dashboard /> : <Navigate to="/auth" />} />
                        <Route path="/profile" element={user ? <Profile /> : <Navigate to="/auth" />} />
                        <Route path="/statistics" element={user ? <Statistics /> : <Navigate to="/auth" />} />
                    </Routes>
                </main>
            </div>
        </Router>
    )
}

export default App
