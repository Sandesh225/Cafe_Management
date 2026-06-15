import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Coffee, LayoutDashboard, UtensilsCrossed, Settings } from 'lucide-react';
import POS from './components/POS';
import KDS from './components/KDS';
import ManagerDashboard from './components/ManagerDashboard';
import './index.css';

function Sidebar() {
  return (
    <div className="sidebar">
      <div className="flex-row" style={{ gap: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ background: 'var(--primary)', padding: '0.5rem', borderRadius: 'var(--radius-sm)' }}>
          <Coffee size={24} color="white" />
        </div>
        <h2 style={{ color: 'white', margin: 0 }}>Cafe CMS</h2>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
          <LayoutDashboard size={20} />
          <span>Point of Sale</span>
        </NavLink>
        <NavLink to="/kds" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <UtensilsCrossed size={20} />
          <span>Kitchen Display</span>
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Settings size={20} />
          <span>Manager Dashboard</span>
        </NavLink>
      </nav>
      
      <div style={{ marginTop: 'auto', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
        <img src="/hero-art.png" alt="Cafe Art" className="hero-image animate-float" />
        <div className="text-muted">
          <small>Staff: Admin</small>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<POS />} />
            <Route path="/kds" element={<KDS />} />
            <Route path="/dashboard" element={<ManagerDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
