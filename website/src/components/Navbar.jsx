import { Link, useLocation } from 'react-router-dom';
import { auth } from '../firebase';
import { Home, BarChart2, User, LogOut, Shield } from 'lucide-react';
import { motion } from 'framer-motion';
import './Components.css';

const Navbar = ({ user }) => {
    const location = useLocation();

    const handleLogout = () => {
        auth.signOut();
    };

    const navItems = [
        { path: '/', icon: <Home size={20} />, label: 'Dashboard' },
        { path: '/statistics', icon: <BarChart2 size={20} />, label: 'Statistics' },
        { path: '/profile', icon: <User size={20} />, label: 'Profile' },
    ];

    return (
        <nav className="navbar glass-card">
            <div className="nav-brand">
                <Shield className="brand-icon" />
                <span>Guardian AI</span>
            </div>

            <div className="nav-links">
                {navItems.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                    >
                        {item.icon}
                        <span className="nav-label">{item.label}</span>
                        {location.pathname === item.path && (
                            <motion.div
                                layoutId="nav-active"
                                className="nav-active-indicator"
                            />
                        )}
                    </Link>
                ))}
            </div>

            <button onClick={handleLogout} className="logout-btn">
                <LogOut size={20} />
                <span>Logout</span>
            </button>
        </nav>
    );
};

export default Navbar;
