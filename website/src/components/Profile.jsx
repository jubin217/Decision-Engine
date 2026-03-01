import { auth } from '../firebase';
import { User, Mail, Calendar, Shield, Settings } from 'lucide-react';
import { motion } from 'framer-motion';
import './Components.css';

const Profile = () => {
    const user = auth.currentUser;

    if (!user) return null;

    const profileData = [
        { icon: <User size={20} />, label: 'Display Name', value: user.displayName || 'Not set' },
        { icon: <Mail size={20} />, label: 'Email Address', value: user.email },
        { icon: <Calendar size={20} />, label: 'Joined', value: user.metadata.creationTime ? new Date(user.metadata.creationTime).toLocaleDateString() : 'N/A' },
        { icon: <Shield size={20} />, label: 'Security Level', value: 'High (Guardian AI Active)' },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="profile-container"
        >
            <div className="profile-header glass-card">
                <div className="avatar">
                    {user.displayName ? user.displayName.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="header-info">
                    <h2>{user.displayName || 'User'}</h2>
                    <p>Verified Guardian</p>
                </div>
                <button className="edit-btn"><Settings size={20} /> Edit Profile</button>
            </div>

            <div className="profile-details">
                {profileData.map((item, index) => (
                    <div key={index} className="detail-card glass-card">
                        <div className="detail-icon">{item.icon}</div>
                        <div className="detail-info">
                            <span className="detail-label">{item.label}</span>
                            <span className="detail-value">{item.value}</span>
                        </div>
                    </div>
                ))}
            </div>
        </motion.div>
    );
};

export default Profile;
