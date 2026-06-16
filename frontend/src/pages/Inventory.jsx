import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { useAuth } from '../context/AuthContext';
import { AlertTriangle, CheckCircle, ChevronDown, ChevronUp, Edit2, Check, X, TrendingDown, TrendingUp, RefreshCw } from 'lucide-react';

const txnColor = (type) => {
  if (type === 'PURCHASE') return 'var(--success)';
  if (type?.includes('SALE') || type === 'CONSUMPTION') return '#f87171';
  if (type?.includes('ADJUSTMENT')) return 'var(--warning)';
  return 'var(--text-secondary)';
};

const txnSign = (qty) => qty >= 0 ? `+${qty.toFixed(3)}` : qty.toFixed(3);

const StockBar = ({ stock, reorder }) => {
  // Show 0–100% where reorder level is 30% of bar
  const max = Math.max(stock, reorder * 3, 1);
  const pct = Math.min((stock / max) * 100, 100);
  const isLow = stock <= reorder;
  return (
    <div style={{ background: 'rgba(255,255,255,0.06)', borderRadius: '99px', height: '6px', width: '100%', overflow: 'hidden' }}>
      <div style={{
        height: '100%', borderRadius: '99px',
        width: `${Math.max(pct, 2)}%`,
        background: isLow
          ? 'linear-gradient(90deg,#f87171,#ef4444)'
          : 'linear-gradient(90deg,var(--success),#34d399)',
        transition: 'width 0.5s ease'
      }} />
    </div>
  );
};

const Inventory = () => {
  const { user } = useAuth();
  const isAdmin = user?.is_admin;

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);
  const [editing, setEditing] = useState(null);   // item id being edited
  const [editVal, setEditVal] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchItems = () => {
    setLoading(true);
    client.get('inventory/')
      .then(res => { setItems(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchItems(); }, []);

  const startEdit = (item) => {
    setEditing(item.id);
    setEditVal(item.reorder_level.toString());
  };

  const saveEdit = (item) => {
    const newVal = parseFloat(editVal);
    if (isNaN(newVal) || newVal < 0) return;
    setSaving(true);
    client.put('inventory/', { id: item.id, reorder_level: newVal })
      .then(() => { fetchItems(); setEditing(null); setSaving(false); })
      .catch(() => setSaving(false));
  };

  const lowCount = items.filter(i => i.status === 'LOW').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1rem' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
        <div>
          <h2 style={{ margin: '0 0 0.2rem', fontSize: '1.2rem' }}>Inventory Items</h2>
          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            {items.length} tracked items
            {lowCount > 0 && (
              <span style={{ marginLeft: '0.75rem', color: 'var(--warning)', fontWeight: 600 }}>
                ⚠ {lowCount} item{lowCount > 1 ? 's' : ''} below reorder level
              </span>
            )}
          </p>
        </div>
        <button className="btn btn-secondary" onClick={fetchItems} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Summary stat cards */}
      <div style={{ display: 'flex', gap: '0.75rem', flexShrink: 0 }}>
        {items.map(item => (
          <div key={item.id} className="card" onClick={() => setExpanded(expanded === item.id ? null : item.id)}
            style={{ flex: '1 1 0', padding: '0.9rem 1rem', cursor: 'pointer', minWidth: 0, transition: 'all 0.2s', border: item.status === 'LOW' ? '1px solid rgba(239,68,68,0.4)' : '1px solid var(--border)', background: expanded === item.id ? 'var(--bg-tertiary)' : '' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>{item.name}</span>
              {item.status === 'LOW'
                ? <AlertTriangle size={14} style={{ color: 'var(--warning)', flexShrink: 0 }} />
                : <CheckCircle size={14} style={{ color: 'var(--success)', flexShrink: 0 }} />}
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 'bold', color: item.status === 'LOW' ? 'var(--warning)' : 'var(--success)', lineHeight: 1, marginBottom: '0.5rem' }}>
              {item.current_stock.toFixed(2)}
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginLeft: '0.3rem' }}>{item.unit}</span>
            </div>
            <StockBar stock={item.current_stock} reorder={item.reorder_level} />
            <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '0.35rem' }}>
              Reorder at {item.reorder_level} {item.unit}
            </div>
          </div>
        ))}
      </div>

      {/* Detail Table */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)', fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', gap: '1rem' }}>
          <span style={{ flex: '0 0 180px' }}>Item</span>
          <span style={{ flex: '1' }}>Current Stock</span>
          <span style={{ flex: '0 0 120px' }}>Unit</span>
          <span style={{ flex: '0 0 160px' }}>Reorder Level</span>
          <span style={{ flex: '0 0 80px' }}>Status</span>
          <span style={{ flex: '0 0 40px' }}></span>
        </div>

        <div style={{ flex: 1, overflowY: 'auto' }}>
          {loading ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading inventory...</div>
          ) : items.map(item => (
            <div key={item.id}>
              {/* Main row */}
              <div
                onClick={() => setExpanded(expanded === item.id ? null : item.id)}
                style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)', cursor: 'pointer', transition: 'background 0.15s', background: expanded === item.id ? 'rgba(255,255,255,0.03)' : '' }}
                onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                onMouseLeave={e => e.currentTarget.style.background = expanded === item.id ? 'rgba(255,255,255,0.03)' : ''}
              >
                <div style={{ flex: '0 0 180px', fontWeight: 600 }}>{item.name}</div>

                {/* Stock with mini bar */}
                <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                  <span style={{ fontWeight: 700, color: item.status === 'LOW' ? 'var(--warning)' : 'var(--success)' }}>
                    {item.current_stock.toFixed(3)}
                  </span>
                  <StockBar stock={item.current_stock} reorder={item.reorder_level} />
                </div>

                <div style={{ flex: '0 0 120px', color: 'var(--text-secondary)' }}>{item.unit}</div>

                {/* Editable reorder level */}
                <div style={{ flex: '0 0 160px' }} onClick={e => e.stopPropagation()}>
                  {isAdmin && editing === item.id ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <input
                        type="number" min="0" step="0.1"
                        value={editVal}
                        onChange={e => setEditVal(e.target.value)}
                        style={{ width: '80px', background: 'var(--bg-tertiary)', border: '1px solid var(--accent-gold)', borderRadius: '6px', color: 'var(--text-primary)', padding: '0.3rem 0.5rem', fontSize: '0.85rem' }}
                        autoFocus
                        onKeyDown={e => { if (e.key === 'Enter') saveEdit(item); if (e.key === 'Escape') setEditing(null); }}
                      />
                      <button onClick={() => saveEdit(item)} disabled={saving}
                        style={{ background: 'var(--success)', border: 'none', borderRadius: '4px', color: '#000', cursor: 'pointer', padding: '0.3rem', display: 'flex' }}>
                        <Check size={14} />
                      </button>
                      <button onClick={() => setEditing(null)}
                        style={{ background: 'rgba(239,68,68,0.2)', border: 'none', borderRadius: '4px', color: 'var(--danger)', cursor: 'pointer', padding: '0.3rem', display: 'flex' }}>
                        <X size={14} />
                      </button>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>{item.reorder_level} {item.unit}</span>
                      {isAdmin && (
                        <button onClick={() => startEdit(item)}
                          style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '0.2rem', display: 'flex', borderRadius: '4px', opacity: 0.6 }}
                          title="Edit reorder level">
                          <Edit2 size={13} />
                        </button>
                      )}
                    </div>
                  )}
                </div>

                <div style={{ flex: '0 0 80px' }}>
                  <span style={{
                    padding: '0.25rem 0.6rem', borderRadius: '99px', fontSize: '0.72rem', fontWeight: 700,
                    background: item.status === 'LOW' ? 'rgba(239,68,68,0.12)' : 'rgba(45,212,168,0.12)',
                    color: item.status === 'LOW' ? 'var(--danger)' : 'var(--success)'
                  }}>
                    {item.status === 'LOW' ? '⚠ LOW' : '✓ OK'}
                  </span>
                </div>

                <div style={{ flex: '0 0 40px', display: 'flex', justifyContent: 'flex-end' }}>
                  {expanded === item.id ? <ChevronUp size={16} style={{ color: 'var(--text-secondary)' }} /> : <ChevronDown size={16} style={{ color: 'var(--text-secondary)' }} />}
                </div>
              </div>

              {/* Expanded: recent transactions */}
              {expanded === item.id && (
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem 1.5rem', borderBottom: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600, marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Recent Transactions
                  </div>
                  {item.transactions.length === 0 ? (
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: 0 }}>No transactions yet. Add stock via Purchases.</p>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      {item.transactions.map((t, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.82rem' }}>
                          <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: t.qty >= 0 ? 'rgba(45,212,168,0.15)' : 'rgba(239,68,68,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                            {t.qty >= 0 ? <TrendingUp size={12} style={{ color: 'var(--success)' }} /> : <TrendingDown size={12} style={{ color: '#f87171' }} />}
                          </div>
                          <span style={{ color: txnColor(t.type), fontWeight: 600, minWidth: '130px' }}>{t.type}</span>
                          <span style={{ color: t.qty >= 0 ? 'var(--success)' : '#f87171', fontWeight: 700, minWidth: '80px' }}>
                            {txnSign(t.qty)} {item.unit}
                          </span>
                          <span style={{ color: 'var(--text-secondary)', minWidth: '100px' }}>{t.ref}</span>
                          <span style={{ color: 'var(--text-secondary)', marginLeft: 'auto' }}>{t.date}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Inventory;
