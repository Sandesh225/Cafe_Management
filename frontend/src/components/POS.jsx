import React, { useState, useEffect } from 'react';
import { ShoppingCart, Plus, Minus, Trash2, X, ChevronLeft } from 'lucide-react';
import Floorplan from './Floorplan';

const API_URL = 'http://localhost:5000'; // Make sure api.py is running on port 5000

const MODIFIERS = {
  milk: [
    { label: 'Whole Milk', price: 0 },
    { label: 'Oat Milk', price: 0.8 },
    { label: 'Almond Milk', price: 0.7 },
    { label: 'Soy Milk', price: 0.5 }
  ],
  syrup: [
    { label: 'Vanilla Syrup', price: 0.5 },
    { label: 'Caramel Syrup', price: 0.5 },
    { label: 'Hazelnut Syrup', price: 0.5 }
  ],
  extra: [
    { label: 'Extra Shot', price: 1.0 },
    { label: 'Whipped Cream', price: 0.5 },
    { label: 'Less Ice', price: 0 }
  ]
};

export default function POS() {
  const [menuItems, setMenuItems] = useState([]);
  const [cart, setCart] = useState([]);
  const [tableId, setTableId] = useState('T1');
  const [customerId, setCustomerId] = useState('CUST-WALKIN');
  
  // Lightning POS state
  const [activeItem, setActiveItem] = useState(null);
  const [selectedMods, setSelectedMods] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/menu`)
      .then(res => res.json())
      .then(data => {
        if (data.items) setMenuItems(data.items);
      })
      .catch(err => console.error("Error fetching menu:", err));
  }, []);

  const handleItemClick = (item) => {
    if (item.category === 'Coffee' || item.category === 'Tea' || item.category === 'General') {
      setActiveItem(item);
      setSelectedMods([]);
    } else {
      addToCart(item);
    }
  };

  const toggleMod = (mod) => {
    setSelectedMods(prev => {
      const exists = prev.find(m => m.label === mod.label);
      if (exists) return prev.filter(m => m.label !== mod.label);
      if (MODIFIERS.milk.find(m => m.label === mod.label)) {
        const filtered = prev.filter(m => !MODIFIERS.milk.find(x => x.label === m.label));
        return [...filtered, mod];
      }
      return [...prev, mod];
    });
  };

  const confirmItemAdd = () => {
    const extraPrice = selectedMods.reduce((sum, mod) => sum + mod.price, 0);
    const modNames = selectedMods.map(m => m.label).join(', ');
    
    const finalItem = {
      ...activeItem,
      name: modNames ? `${activeItem.name} (${modNames})` : activeItem.name,
      price: activeItem.price + extraPrice,
      baseName: activeItem.name
    };
    addToCart(finalItem);
  };

  const addToCart = (item) => {
    setActiveItem(null);
    setSelectedMods([]);
    setCart(prev => {
      const existing = prev.find(i => i.name === item.name);
      if (existing) {
        return prev.map(i => i.name === item.name ? { ...i, qty: i.qty + 1 } : i);
      }
      return [...prev, { ...item, qty: 1 }];
    });
  };

  const updateQty = (name, delta) => {
    setCart(prev => prev.map(i => {
      if (i.name === name) {
        return { ...i, qty: Math.max(0, i.qty + delta) };
      }
      return i;
    }).filter(i => i.qty > 0));
  };

  const clearCart = () => setCart([]);

  const checkout = async () => {
    if (cart.length === 0) return alert('Cart is empty!');
    if (!tableId) return alert('Please select a table!');
    
    const payload = {
      customer_id: customerId,
      table_id: tableId,
      staff_id: 'admin',
      items: cart.map(i => ({ name: i.name, qty: i.qty }))
    };

    try {
      const res = await fetch(`${API_URL}/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      
      if (res.ok) {
        // Trigger a re-render of floorplan by just resetting tableId or leaving it
        setTableId('');
        clearCart();
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (err) {
      alert(`Failed to place order: ${err}`);
    }
  };

  const total = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);

  return (
    <div className="pos-layout animate-fade-in">
      {/* Menu & Floorplan Area */}
      <div>
        <Floorplan onSelectTable={setTableId} currentTable={tableId} />

        <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
          <h2>Menu Categories</h2>
          <input 
            type="text" 
            value={customerId} 
            onChange={e => setCustomerId(e.target.value)} 
            placeholder="Customer ID"
            style={{ padding: '0.5rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', background: 'var(--bg-surface)', color: 'white' }}
          />
        </div>

        <div className="menu-grid">
          {menuItems.map(item => (
            <div key={item.name} className="menu-item-card" onClick={() => handleItemClick(item)} style={{ background: activeItem?.name === item.name ? 'var(--primary)' : undefined }}>
              <div className="text-muted" style={{ fontSize: '0.875rem', color: activeItem?.name === item.name ? 'rgba(255,255,255,0.7)' : undefined }}>{item.category}</div>
              <h3 style={{ margin: '0.5rem 0', color: activeItem?.name === item.name ? 'white' : undefined }}>{item.name}</h3>
              <div style={{ color: activeItem?.name === item.name ? 'white' : 'var(--accent-success)', fontWeight: 'bold' }}>${item.price.toFixed(2)}</div>
            </div>
          ))}
          {menuItems.length === 0 && (
            <div className="text-muted">Loading menu items... (Ensure backend is running)</div>
          )}
        </div>
      </div>

      {/* Lightning POS Sidebar */}
      <div className="glass-panel" style={{ padding: '0', height: 'calc(100vh - 4rem)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        
        {/* MODIFIER VIEW */}
        {activeItem ? (
          <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)' }}>
              <button onClick={() => setActiveItem(null)} className="flex-row text-muted" style={{ gap: '0.5rem', marginBottom: '1rem', background: 'none', border: 'none', padding: 0, cursor: 'pointer' }}>
                <ChevronLeft size={20} /> Back to Cart
              </button>
              <h2 style={{ margin: 0 }}>Customize {activeItem.name}</h2>
            </div>

            <div style={{ padding: '1.5rem', flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              {/* Milk */}
              <div>
                <h3 className="text-muted" style={{ marginBottom: '1rem', fontSize: '1rem' }}>Milk</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  {MODIFIERS.milk.map(mod => {
                    const isSelected = selectedMods.find(m => m.label === mod.label);
                    return (
                      <button key={mod.label} onClick={() => toggleMod(mod)} style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: isSelected ? 'var(--primary)' : 'rgba(255,255,255,0.05)', border: `1px solid ${isSelected ? 'var(--primary)' : 'var(--border-color)'}`, color: 'white', textAlign: 'left', cursor: 'pointer', transition: 'all 0.1s' }}>
                        <div style={{ fontWeight: 600 }}>{mod.label}</div>
                        <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>{mod.price > 0 ? `+$${mod.price.toFixed(2)}` : 'Included'}</div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Syrups & Extras */}
              <div>
                <h3 className="text-muted" style={{ marginBottom: '1rem', fontSize: '1rem' }}>Syrups & Extras</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  {[...MODIFIERS.syrup, ...MODIFIERS.extra].map(mod => {
                    const isSelected = selectedMods.find(m => m.label === mod.label);
                    return (
                      <button key={mod.label} onClick={() => toggleMod(mod)} style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: isSelected ? 'var(--primary)' : 'rgba(255,255,255,0.05)', border: `1px solid ${isSelected ? 'var(--primary)' : 'var(--border-color)'}`, color: 'white', textAlign: 'left', cursor: 'pointer', transition: 'all 0.1s' }}>
                        <div style={{ fontWeight: 600 }}>{mod.label}</div>
                        <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>{mod.price > 0 ? `+$${mod.price.toFixed(2)}` : 'Free'}</div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)' }}>
              <button className="btn-success" style={{ width: '100%', padding: '1.25rem', fontSize: '1.25rem' }} onClick={confirmItemAdd}>
                Add • ${(activeItem.price + selectedMods.reduce((s, m) => s + m.price, 0)).toFixed(2)}
              </button>
            </div>
          </div>
        ) : (
          /* CART VIEW */
          <div className="cart-panel animate-fade-in" style={{ padding: '1.5rem', height: '100%' }}>
            <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
              <h2 className="flex-row" style={{ gap: '0.5rem' }}><ShoppingCart size={24} /> Order Cart</h2>
              <button className="btn-danger" onClick={clearCart}><Trash2 size={18} /></button>
            </div>

            <div className="text-muted" style={{ marginBottom: '1rem', background: 'rgba(255,255,255,0.05)', padding: '0.5rem', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
              Table: <strong style={{ color: 'white' }}>{tableId || 'None Selected'}</strong>
            </div>

            <div className="cart-items">
              {cart.map(item => (
                <div key={item.name} className="cart-item animate-fade-in">
                  <div style={{ flex: 1, paddingRight: '0.5rem' }}>
                    <div style={{ fontWeight: 600, wordBreak: 'break-word', lineHeight: '1.2' }}>{item.name}</div>
                    <div className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>${item.price.toFixed(2)} each</div>
                  </div>
                  <div className="flex-row" style={{ gap: '0.75rem', background: 'var(--bg-color)', padding: '0.25rem', borderRadius: 'var(--radius-md)' }}>
                    <button onClick={() => updateQty(item.name, -1)} style={{ color: 'white', padding: '0.25rem' }}><Minus size={16} /></button>
                    <span style={{ fontWeight: 600, width: '20px', textAlign: 'center' }}>{item.qty}</span>
                    <button onClick={() => updateQty(item.name, 1)} style={{ color: 'white', padding: '0.25rem' }}><Plus size={16} /></button>
                  </div>
                </div>
              ))}
              {cart.length === 0 && (
                <div className="text-muted" style={{ textAlign: 'center', marginTop: '2rem' }}>
                  Cart is empty
                </div>
              )}
            </div>

            <div className="cart-summary">
              <div className="flex-between">
                <span className="text-muted">Subtotal</span>
                <span>${total.toFixed(2)}</span>
              </div>
              <div className="flex-between" style={{ fontSize: '1.25rem', fontWeight: 700 }}>
                <span>Total</span>
                <span style={{ color: 'var(--accent-success)' }}>${total.toFixed(2)}</span>
              </div>
              <button className="btn-primary" style={{ width: '100%', marginTop: '1rem', padding: '1.25rem', fontSize: '1.25rem' }} onClick={checkout} disabled={cart.length === 0 || !tableId}>
                Process Payment
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
