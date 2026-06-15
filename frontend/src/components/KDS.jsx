import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, ChefHat, AlertCircle, Coffee, UtensilsCrossed } from 'lucide-react';

const API_URL = 'http://localhost:5000';

export default function KDS() {
  const [tickets, setTickets] = useState([]);
  const [now, setNow] = useState(new Date());
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'barista', 'kitchen'

  const fetchQueue = () => {
    fetch(`${API_URL}/queue`)
      .then(res => res.json())
      .then(data => {
        if (data.tickets) {
          const sorted = data.tickets.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
          setTickets(sorted);
        }
      })
      .catch(err => console.error("Error fetching KDS queue:", err));
  };

  useEffect(() => {
    fetchQueue();
    const dataInterval = setInterval(fetchQueue, 5000);
    const timeInterval = setInterval(() => setNow(new Date()), 1000);
    return () => {
      clearInterval(dataInterval);
      clearInterval(timeInterval);
    };
  }, []);

  const getElapsedTime = (createdAtStr) => {
    const created = new Date(createdAtStr);
    const diff = Math.max(0, Math.floor((now - created) / 1000));
    const mins = Math.floor(diff / 60);
    const secs = diff % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status) => {
    const s = (status || '').toLowerCase();
    if (s === 'ready') return 'var(--accent-success)';
    if (s === 'in_progress' || s === 'in progress') return '#3B82F6';
    return 'var(--accent-warning)';
  };

  const markStatus = async (ticketId, status) => {
    try {
      const res = await fetch(`${API_URL}/queue/${ticketId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      if (res.ok) {
        fetchQueue();
      }
    } catch (err) {
      console.error("Failed to update status", err);
    }
  };

  const filteredTickets = tickets.filter(t => {
    const s = (t.status || '').toLowerCase();
    if (s === 'served') return false;
    
    if (activeTab === 'barista') return t.ticket_id.includes('-BARISTA');
    if (activeTab === 'kitchen') return t.ticket_id.includes('-KITCHEN');
    return true;
  });

  return (
    <div className="animate-fade-in" style={{ padding: '1rem' }}>
      <div className="flex-between" style={{ marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
        <h1 className="flex-row" style={{ gap: '0.75rem' }}>
          <ChefHat size={32} color="var(--primary)" />
          Kitchen Display System
        </h1>
        
        <div className="flex-row" style={{ gap: '0.5rem', background: 'rgba(0,0,0,0.2)', padding: '0.25rem', borderRadius: 'var(--radius-xl)' }}>
          <button 
            onClick={() => setActiveTab('all')}
            style={{ padding: '0.5rem 1rem', borderRadius: 'var(--radius-lg)', background: activeTab === 'all' ? 'var(--primary)' : 'transparent', color: 'white' }}>
            All Stations
          </button>
          <button 
            onClick={() => setActiveTab('barista')}
            className="flex-row"
            style={{ gap: '0.5rem', padding: '0.5rem 1rem', borderRadius: 'var(--radius-lg)', background: activeTab === 'barista' ? 'var(--primary)' : 'transparent', color: 'white' }}>
            <Coffee size={18} /> Barista
          </button>
          <button 
            onClick={() => setActiveTab('kitchen')}
            className="flex-row"
            style={{ gap: '0.5rem', padding: '0.5rem 1rem', borderRadius: 'var(--radius-lg)', background: activeTab === 'kitchen' ? 'var(--primary)' : 'transparent', color: 'white' }}>
            <UtensilsCrossed size={18} /> Kitchen
          </button>
        </div>
      </div>

      <div className="grid-layout" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '2rem', alignItems: 'start' }}>
        {filteredTickets.map(ticket => {
          const statusLower = (ticket.status || '').toLowerCase();
          const color = getStatusColor(ticket.status);
          const isUrgent = (now - new Date(ticket.created_at)) / 1000 > 600;

          // Remove the routing tag from display
          const displayId = ticket.ticket_id.split('-')[0].toUpperCase();
          const routeType = ticket.ticket_id.includes('-BARISTA') ? 'Barista' : ticket.ticket_id.includes('-KITCHEN') ? 'Kitchen' : 'General';

          return (
            <div key={ticket.ticket_id} className="glass-panel animate-fade-in" style={{ 
              display: 'flex', flexDirection: 'column', 
              borderTop: `5px solid ${color}`,
              boxShadow: isUrgent && statusLower !== 'ready' ? '0 0 15px rgba(239, 68, 68, 0.2)' : undefined
            }}>
              <div style={{ padding: '1.25rem', borderBottom: '1px solid var(--border-color)' }}>
                <div className="flex-between" style={{ marginBottom: '0.5rem' }}>
                  <div className="flex-row" style={{ gap: '0.5rem' }}>
                    <h2 style={{ margin: 0, fontSize: '1.5rem', fontFamily: 'monospace' }}>#{displayId}</h2>
                    <span style={{ fontSize: '0.75rem', background: 'rgba(255,255,255,0.1)', padding: '0.2rem 0.5rem', borderRadius: 'var(--radius-sm)' }}>{routeType}</span>
                  </div>
                  <div style={{ background: 'var(--primary)', color: 'white', padding: '0.25rem 0.75rem', borderRadius: 'var(--radius-md)', fontWeight: 'bold' }}>
                    {ticket.table_label}
                  </div>
                </div>
                
                <div className="flex-between" style={{ fontSize: '0.9rem', color: isUrgent && statusLower !== 'ready' ? 'var(--accent-danger)' : 'var(--text-muted)', fontWeight: 500 }}>
                  <div className="flex-row" style={{ gap: '0.5rem' }}>
                    {isUrgent && statusLower !== 'ready' ? <AlertCircle size={16} /> : <Clock size={16} />}
                    <span>{getElapsedTime(ticket.created_at)}</span>
                  </div>
                  <span style={{ color, textTransform: 'uppercase', letterSpacing: '1px', fontSize: '0.8rem' }}>
                    {ticket.status.replace('_', ' ')}
                  </span>
                </div>
              </div>

              <div style={{ padding: '1.5rem', flex: 1 }}>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {Array.isArray(ticket.items) ? (
                    ticket.items.map((item, idx) => (
                      <li key={idx} className="flex-row" style={{ fontSize: '1.15rem', gap: '1rem', alignItems: 'flex-start' }}>
                        <span style={{ background: 'rgba(255,255,255,0.1)', padding: '0.2rem 0.6rem', borderRadius: 'var(--radius-sm)', fontWeight: 'bold', minWidth: '40px', textAlign: 'center' }}>
                          {item.qty || 1}x
                        </span>
                        <span style={{ paddingTop: '0.2rem', fontWeight: 500 }}>{item.name || item.item || 'Item'}</span>
                      </li>
                    ))
                  ) : (
                    Object.entries(ticket.items || {}).map(([itemName, qty]) => {
                      const quantity = typeof qty === 'object' ? (qty.qty || 1) : qty;
                      const name = typeof qty === 'object' ? (qty.name || itemName) : itemName;
                      return (
                        <li key={name} className="flex-row" style={{ fontSize: '1.15rem', gap: '1rem', alignItems: 'flex-start' }}>
                          <span style={{ background: 'rgba(255,255,255,0.1)', padding: '0.2rem 0.6rem', borderRadius: 'var(--radius-sm)', fontWeight: 'bold', minWidth: '40px', textAlign: 'center' }}>
                            {quantity}x
                          </span>
                          <span style={{ paddingTop: '0.2rem', fontWeight: 500 }}>{name}</span>
                        </li>
                      );
                    })
                  )}
                </ul>
              </div>

              <div style={{ padding: '1.25rem', background: 'rgba(0,0,0,0.2)', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '1rem' }}>
                {(statusLower === 'queued' || statusLower === 'in_progress') && (
                  <button className="btn-success" style={{ flex: 1, padding: '1rem', fontSize: '1.1rem', background: '#3B82F6', boxShadow: '0 4px 14px 0 rgba(59, 130, 246, 0.39)' }} onClick={() => markStatus(ticket.ticket_id, 'ready')}>
                    Mark Ready
                  </button>
                )}
                {statusLower === 'ready' && (
                  <button className="btn-success" style={{ flex: 1, padding: '1rem', fontSize: '1.1rem', display: 'flex', justifyContent: 'center', gap: '0.5rem' }} onClick={() => markStatus(ticket.ticket_id, 'served')}>
                    <CheckCircle size={22} /> Serve Order
                  </button>
                )}
              </div>
            </div>
          );
        })}
        {filteredTickets.length === 0 && (
          <div className="glass-panel" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '4rem 2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            <CheckCircle size={48} color="var(--text-muted)" style={{ opacity: 0.5 }} />
            <h2 className="text-muted">All caught up!</h2>
            <p className="text-muted">No active orders in this queue.</p>
          </div>
        )}
      </div>
    </div>
  );
}
