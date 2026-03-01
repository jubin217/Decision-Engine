import { useState, useEffect } from 'react';
import { db } from '../firebase';
import { collection, query, onSnapshot } from 'firebase/firestore';
import { BarChart, TrendingUp, AlertCircle, PieChart } from 'lucide-react';
import { motion } from 'framer-motion';
import './Components.css';

const Statistics = () => {
    const [stats, setStats] = useState({
        total: 0,
        byType: {},
        byDay: []
    });

    useEffect(() => {
        const q = query(collection(db, 'emergencies'));

        const unsubscribe = onSnapshot(q, (snapshot) => {
            const data = snapshot.docs.map(doc => doc.data());

            const typeMap = {};
            const dayMap = {};

            data.forEach(item => {
                const type = item.reason?.includes('Fall') ? 'Fall' : (item.reason?.includes('Voice') ? 'Voice' : 'Other');
                typeMap[type] = (typeMap[type] || 0) + 1;

                const date = new Date(item.timestamp?.toMillis()).toLocaleDateString();
                dayMap[date] = (dayMap[date] || 0) + 1;
            });

            setStats({
                total: data.length,
                byType: typeMap,
                byDay: Object.entries(dayMap).map(([date, count]) => ({ date, count })).slice(-7)
            });
        });

        return () => unsubscribe();
    }, []);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="stats-container"
        >
            <div className="stats-header">
                <h1><TrendingUp /> Analytical Overview</h1>
                <p>Comprehensive report of system triggers and performance</p>
            </div>

            <div className="stats-grid">
                <div className="stat-summary glass-card">
                    <div className="main-total">
                        <span className="total-number">{stats.total}</span>
                        <span className="total-label">Total Emergencies Logged</span>
                    </div>
                    <div className="type-breakdown">
                        {Object.entries(stats.byType).map(([type, count]) => (
                            <div key={type} className="type-item">
                                <span className="type-name">{type}</span>
                                <div className="progress-bar">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${(count / stats.total) * 100}%` }}
                                        className={`progress-fill ${type === 'Fall' ? 'bg-danger' : 'bg-primary'}`}
                                    ></motion.div>
                                </div>
                                <span className="type-count">{count}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="chart-section glass-card">
                    <h3>Last 7 Days Activity</h3>
                    <div className="simple-bar-chart">
                        {stats.byDay.length === 0 ? (
                            <div className="no-data">Insufficient data for charting</div>
                        ) : (
                            stats.byDay.map((item, i) => (
                                <div key={i} className="bar-group">
                                    <motion.div
                                        initial={{ height: 0 }}
                                        animate={{ height: `${(item.count / Math.max(...stats.byDay.map(d => d.count))) * 150}px` }}
                                        className="bar-fill primary-gradient"
                                    />
                                    <span className="bar-label">{item.date.split('/')[0]}/{item.date.split('/')[1]}</span>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default Statistics;
