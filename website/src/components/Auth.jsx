import { useState } from 'react';
import { auth } from '../firebase';
import {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    updateProfile
} from 'firebase/auth';
import { LogIn, UserPlus, ShieldCheck, Mail, Lock, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './Components.css';

const Auth = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [displayName, setDisplayName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (isLogin) {
                await signInWithEmailAndPassword(auth, email, password);
            } else {
                const userCredential = await createUserWithEmailAndPassword(auth, email, password);
                await updateProfile(userCredential.user, { displayName });
            }
        } catch (err) {
            setError(err.message.replace('Firebase: ', ''));
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="auth-card glass-card"
        >
            <div className="auth-header">
                <ShieldCheck className="auth-logo" size={48} />
                <h2>Guardian AI</h2>
                <p>{isLogin ? 'Welcome back, Safety First!' : 'Join the safety network'}</p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
                <AnimatePresence mode='wait'>
                    {!isLogin && (
                        <motion.div
                            key="name"
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="input-group"
                        >
                            <User className="input-icon" size={20} />
                            <input
                                type="text"
                                placeholder="Full Name"
                                value={displayName}
                                onChange={(e) => setDisplayName(e.target.value)}
                                required={!isLogin}
                            />
                        </motion.div>
                    )}
                </AnimatePresence>

                <div className="input-group">
                    <Mail className="input-icon" size={20} />
                    <input
                        type="email"
                        placeholder="Email Address"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>

                <div className="input-group">
                    <Lock className="input-icon" size={20} />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>

                {error && <div className="auth-error">{error}</div>}

                <button type="submit" disabled={loading} className="submit-btn primary-gradient">
                    {loading ? 'Processing...' : (isLogin ? 'Login' : 'Sign Up')}
                    {isLogin ? <LogIn size={20} /> : <UserPlus size={20} />}
                </button>
            </form>

            <div className="auth-footer">
                <button onClick={() => setIsLogin(!isLogin)} className="toggle-btn">
                    {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Login"}
                </button>
            </div>
        </motion.div>
    );
};

export default Auth;
