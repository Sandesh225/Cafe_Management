import React, { useState, useEffect } from 'react';
import { Armchair } from 'lucide-react';

const API_URL = 'http://localhost:5000';

export default function Floorplan({ onSelectTable, currentTable }) {
  const [tables, setTables] = useState([]);

  useEffect(() => {
    fetchTables();
    const interval = setInterval(fetchTables, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchTables = () => {
    fetch(`${API_URL}/tables`)
      .then(res => res.json())
      .then(data => {
        if (data.tables) setTables(data.tables);
      })
      .catch(console.error);
  };

  const handleTableClick = async (table) => {
    if (table.status === 'occupied') {
      const confirmClear = window.confirm(`Table ${table.label} is occupied. Clear it to open it up?`);
      if (confirmClear) {
        await fetch(`${API_URL}/tables/${table.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'free' })
        });
        fetchTables();
      }
    } else {
      onSelectTable(table.id);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
      <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>Cafe Floorplan</h2>
      
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        {tables.map(table => {
          const isOccupied = table.status === 'occupied';
          const isSelected = currentTable === table.id;
          
          return (
            <button 
              key={table.id}
              onClick={() => handleTableClick(table)}
              style={{
                width: '80px',
                height: '80px',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.25rem',
                border: isSelected ? '2px solid white' : `1px solid ${isOccupied ? 'rgba(239,68,68,0.5)' : 'rgba(16,185,129,0.5)'}`,
                background: isOccupied ? 'rgba(239,68,68,0.1)' : (isSelected ? 'var(--primary)' : 'rgba(16,185,129,0.1)'),
                color: 'white',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <Armchair size={24} color={isSelected ? 'white' : (isOccupied ? 'var(--accent-danger)' : 'var(--accent-success)')} />
              <span style={{ fontWeight: 600 }}>{table.label}</span>
            </button>
          );
        })}
      </div>
      
      <div className="flex-row" style={{ gap: '1.5rem', marginTop: '1.5rem', fontSize: '0.875rem' }}>
        <div className="flex-row" style={{ gap: '0.5rem' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--accent-success)' }} />
          <span className="text-muted">Open</span>
        </div>
        <div className="flex-row" style={{ gap: '0.5rem' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--accent-danger)' }} />
          <span className="text-muted">Occupied</span>
        </div>
        <div className="flex-row" style={{ gap: '0.5rem' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--primary)' }} />
          <span className="text-muted">Selected</span>
        </div>
      </div>
    </div>
  );
}
