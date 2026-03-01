import { useState, useEffect } from 'react';
import { db } from '../firebase';
import { collection, query, orderBy, onSnapshot, limit } from 'firebase/firestore';
import { AlertTriangle, Activity, Shield, Clock, MapPin } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './Components.css';

const Dashboard = () => {
    const [emergencies, setEmergencies] = useState([]);
    const [latestEmergency, setLatestEmergency] = useState(null);
    const [totalEmergencies, setTotalEmergencies] = useState(0);

    useEffect(() => {
        const q = query(collection(db, 'emergencies'), orderBy('timestamp', 'desc'));

        const unsubscribe = onSnapshot(q, (snapshot) => {
            console.log("🔥 Received Firestore snapshot update");
            const data = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            }));
            console.log("📊 Records found:", data.length);
            setEmergencies(data);
            setTotalEmergencies(data.length);

            // Check for new emergency in the last 10 seconds for the "Big Alert"
            if (data.length > 0) {
                const latest = data[0];
                const now = Date.now();
                const emergencyTime = latest.timestamp?.toMillis() || now;

                console.log("🚨 Latest emergency time:", new Date(emergencyTime).toLocaleString());

                if (now - emergencyTime < 10000) {
                    console.log("🔔 Triggering BIG ALERT overlay");
                    setLatestEmergency(latest);
                    // Auto-dismiss alert after 10 seconds
                    setTimeout(() => setLatestEmergency(null), 10000);
                }
            }
        }, (error) => {
            console.error("❌ Firestore Subscription Error:", error);
        });

        return () => unsubscribe();
    }, []);

    return (
        <div className="dashboard-grid">
            {/* Big Alert Overlay */}
            <AnimatePresence>
                {latestEmergency && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8, y: 100 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.8, y: 100 }}
                        className="big-alert-overlay"
                    >
                        <div className="alert-content glass-card danger-border">
                            <AlertTriangle className="alert-icon pulse" size={80} />
                            <h1>EMERGENCY TRIGGERED</h1>
                            <p className="reason">{latestEmergency.reason}</p>
                            <div className="alert-meta">
                                <span><Clock size={16} /> {new Date(latestEmergency.timestamp?.toMillis()).toLocaleTimeString()}</span>
                                {latestEmergency.location && <span><MapPin size={16} /> {latestEmergency.location}</span>}
                            </div>
                            <button onClick={() => setLatestEmergency(null)} className="dismiss-btn">
                                Acknowledge Alert
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Stats Cards */}
            <div className="stats-row">
                <div className="stat-card glass-card debug-card">
                    <button
                        onClick={async () => {
                            const { addDoc, collection, serverTimestamp } = await import('firebase/firestore');
                            try {
                                await addDoc(collection(db, 'emergencies'), {
                                    reason: "Manual Test Alert",
                                    timestamp: serverTimestamp(),
                                    type: "TEST",
                                    location: "Web UI"
                                });
                                alert("✅ Test emergency sent to Firestore!");
                            } catch (e) {
                                console.error(e);
                                alert("❌ Error sending test: " + e.message);
                            }
                        }}
                        className="test-btn"
                    >
                        Test Firestore Sync
                    </button>
                </div>
                <motion.div whileHover={{ y: -5 }} className="stat-card glass-card">
                    <Shield className="stat-icon" size={24} />
                    <div className="stat-info">
                        <span className="stat-label">System Status</span>
                        <span className="stat-value text-success">Active & Monitoring</span>
                    </div>
                </motion.div>

                <motion.div whileHover={{ y: -5 }} className="stat-card glass-card">
                    <AlertTriangle className="stat-icon text-danger" size={24} />
                    <div className="stat-info">
                        <span className="stat-label">Total Emergencies</span>
                        <span className="stat-value">{totalEmergencies}</span>
                    </div>
                </motion.div>

                <motion.div whileHover={{ y: -5 }} className="stat-card glass-card">
                    <Activity className="stat-icon text-primary" size={24} />
                    <div className="stat-info">
                        <span className="stat-label">Detection Modules</span>
                        <span className="stat-value">Fall + Voice</span>
                    </div>
                </motion.div>
            </div>

            {/* Emergency History */}
            <div className="history-section glass-card">
                <h3>Emergency History</h3>
                <div className="history-list">
                    {emergencies.length === 0 ? (
                        <div className="no-data">No emergencies detected yet. System is safe.</div>
                    ) : (
                        emergencies.map((e) => (
                            <div key={e.id} className="history-item">
                                <div className="item-status danger"></div>
                                <div className="item-details">
                                    <span className="item-reason">{e.reason}</span>
                                    <span className="item-time">
                                        {e.timestamp?.toDate().toLocaleString()}
                                    </span>
                                </div>
                                <div className="item-type">Critical</div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
