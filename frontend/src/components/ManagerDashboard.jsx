import React, { useState, useEffect } from 'react';
import { TrendingUp, PackageSearch, Users, Activity } from 'lucide-react';

const API_URL = 'http://localhost:5000';

export default function ManagerDashboard() {
  const [stats, setStats] = useState({
    dailyRevenue: 0,
    totalOrders: 0
  });

  useEffect(() => {
    // Fetch daily summary
    fetch(`${API_URL}/report/daily`)
      .then(res => res.json())
      .then(data => {
        if (!data.error) {
          setStats({
            dailyRevenue: data.net_revenue || 0,
            totalOrders: data.total_orders || 0
          });
        }
      })
      .catch(console.error);
  }, []);

  return (
    <div className="animate-fade-in" style={{ padding: '1rem' }}>
      <div style={{ marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
        <h1>Manager Dashboard</h1>
        <p className="text-muted">Overview of today's cafe operations.</p>
      </div>

      <div className="grid-layout" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.2)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
            <TrendingUp size={32} color="var(--accent-success)" />
          </div>
          <div>
            <div className="text-muted">Today's Revenue</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>${stats.dailyRevenue.toFixed(2)}</div>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ background: 'rgba(79, 70, 229, 0.2)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
            <Activity size={32} color="var(--primary)" />
          </div>
          <div>
            <div className="text-muted">Total Orders</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.totalOrders}</div>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem', opacity: 0.5 }}>
          <div style={{ background: 'rgba(245, 158, 11, 0.2)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
            <PackageSearch size={32} color="var(--accent-warning)" />
          </div>
          <div>
            <div className="text-muted">Low Stock Alerts</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>--</div>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem', opacity: 0.5 }}>
          <div style={{ background: 'rgba(239, 68, 68, 0.2)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
            <Users size={32} color="var(--accent-danger)" />
          </div>
          <div>
            <div className="text-muted">Staff on Shift</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>--</div>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
        <h2 className="text-muted" style={{ marginBottom: '1rem' }}>Advanced Features Coming Soon</h2>
        <p className="text-muted">Granular inventory tracking, staff schedules, and CRM data will be unlocked in upcoming phases.</p>
      </div>
    </div>
  );
}
