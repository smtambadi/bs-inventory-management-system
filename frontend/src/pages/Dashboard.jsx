import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { AlertCircle, IndianRupee, Package } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const { user } = useAuth();
  const isAdmin = user?.is_admin;
  const [data, setData] = useState({ stock: [], item_sales: [], consumption: [] });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('CHICKEN');
  const [dateFilterType, setDateFilterType] = useState('today');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const fetchDashboardData = () => {
    setLoading(true);
    let query = 'dashboard/';
    if (dateFilterType === 'custom' && (startDate || endDate)) {
      const params = new URLSearchParams();
      if (startDate) params.append('start', startDate);
      if (endDate) params.append('end', endDate);
      query += `?${params.toString()}`;
    } else if (dateFilterType === 'today') {
      const today = new Date().toISOString().split('T')[0];
      query += `?start=${today}&end=${today}`;
    } else if (dateFilterType === 'yesterday') {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const yStr = yesterday.toISOString().split('T')[0];
      query += `?start=${yStr}&end=${yStr}`;
    }
    client.get(query)
      .then(res => { setData(res.data); setLoading(false); })
      .catch(err => { console.error(err); setLoading(false); });
  };

  useEffect(() => { fetchDashboardData(); }, [dateFilterType, startDate, endDate]);

  if (loading) return <div style={{ padding: '2rem', color: 'var(--text-secondary)' }}>Loading dashboard...</div>;

  // ── CASHIER VIEW: only live stock ──
  if (!isAdmin) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexShrink: 0 }}>
          <Package size={22} style={{ color: 'var(--accent-gold)' }} />
          <h2 style={{ margin: 0, fontSize: '1.2rem' }}>Live Stock Overview</h2>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          {data.stock.map(item => (
            <div key={item.id} className="card" style={{ flex: '1 1 160px', padding: '1.25rem', position: 'relative', overflow: 'hidden', minWidth: 0 }}>
              {item.status === 'LOW' && (
                <div style={{ position: 'absolute', top: '0.75rem', right: '0.75rem', color: 'var(--warning)' }}>
                  <AlertCircle size={16} />
                </div>
              )}
              <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '0.4rem', letterSpacing: '0.05em' }}>
                {item.name}
              </h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: item.status === 'LOW' ? 'var(--warning)' : 'var(--success)', lineHeight: 1.1 }}>
                {parseFloat(item.current_stock).toFixed(2)}
                <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginLeft: '0.4rem' }}>{item.unit}</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '0.4rem' }}>
                Reorder Level: {item.reorder_level}
              </div>
              {item.status === 'LOW' && (
                <div style={{ position: 'absolute', bottom: 0, left: 0, width: '100%', height: '3px', backgroundColor: 'var(--warning)' }} />
              )}
            </div>
          ))}
        </div>
        <div className="card" style={{ padding: '1.25rem', background: 'rgba(245,166,35,0.04)', border: '1px solid rgba(245,166,35,0.12)' }}>
          <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            🔒 Sales breakdown and reports are available to administrators only.
          </p>
        </div>
      </div>
    );
  }

  const currentCategoryData = data.item_sales?.filter(item => item.category === activeTab) || [];
  const totalCategoryUnits = currentCategoryData.reduce((sum, item) => sum + parseInt(item.total_qty), 0);
  const totalCategoryAmount = currentCategoryData.reduce((sum, item) => sum + parseFloat(item.total_amount), 0);
  const consumed = data.consumption?.find(c => c.ingredient_name.toUpperCase() === activeTab);
  const consumedQty = consumed ? parseFloat(consumed.consumed_qty).toFixed(2) : '0.00';
  const consumedUnit = data.stock?.find(s => s.name.toUpperCase() === activeTab)?.unit || '';

  const tabs = ['CHICKEN', 'MUTTON', 'BOTI', 'RICE', 'EGG'];

  const chartData = {
    labels: currentCategoryData.map(item => item.name),
    datasets: [{
      label: 'Total Collection (₹)',
      data: currentCategoryData.map(item => item.total_amount),
      backgroundColor: 'rgba(234, 88, 12, 0.8)',
      borderColor: '#ea580c',
      borderWidth: 1,
      borderRadius: 4,
    }],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: (ctx) => `₹${ctx.raw.toLocaleString()}` } }
    },
    scales: {
      y: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
      x: { ticks: { color: '#9ca3af', font: { size: 9 }, maxRotation: 35, minRotation: 35 }, grid: { display: false } }
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '0.75rem' }}>

      {/* ── Top bar ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
        <h2 style={{ margin: 0, fontSize: '1.2rem' }}>Dashboard Overview</h2>
      </div>

      {/* ── Stock Cards Row ── */}
      <div style={{ display: 'flex', gap: '0.75rem', flexShrink: 0 }}>
        {data.stock.map(item => (
          <div key={item.id} className="card" style={{ flex: '1 1 0', padding: '1rem', position: 'relative', overflow: 'hidden', minWidth: 0 }}>
            {item.status === 'LOW' && (
              <div style={{ position: 'absolute', top: '0.75rem', right: '0.75rem', color: 'var(--warning)' }}>
                <AlertCircle size={16} />
              </div>
            )}
            <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '0.3rem', letterSpacing: '0.05em' }}>
              {item.name}
            </h3>
            <div style={{ fontSize: '1.8rem', fontWeight: 'bold', color: item.status === 'LOW' ? 'var(--warning)' : 'var(--success)', lineHeight: 1.1 }}>
              {parseFloat(item.current_stock).toFixed(2)}
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginLeft: '0.3rem' }}>{item.unit}</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
              Reorder: {item.reorder_level}
            </div>
            {item.status === 'LOW' && (
              <div style={{ position: 'absolute', bottom: 0, left: 0, width: '100%', height: '3px', backgroundColor: 'var(--warning)' }} />
            )}
          </div>
        ))}
      </div>

      {/* ── Sales Breakdown Header ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0, flexWrap: 'wrap', gap: '0.5rem' }}>
        <h3 style={{ margin: 0, fontSize: '1rem' }}>Sales Breakdown</h3>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <select
            className="form-control"
            style={{ width: 'auto', marginBottom: 0, fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}
            value={dateFilterType}
            onChange={e => setDateFilterType(e.target.value)}
          >
            <option value="today">Today</option>
            <option value="yesterday">Yesterday</option>
            <option value="custom">Custom Date(s)</option>
          </select>
          {dateFilterType === 'custom' && (
            <>
              <input type="date" className="form-control" style={{ width: 'auto', marginBottom: 0, fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}
                value={startDate} onChange={e => setStartDate(e.target.value)} />
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>to</span>
              <input type="date" className="form-control" style={{ width: 'auto', marginBottom: 0, fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}
                value={endDate} onChange={e => setEndDate(e.target.value)} />
            </>
          )}
        </div>

        <div style={{ display: 'flex', gap: '0.4rem' }}>
          {tabs.map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              background: activeTab === tab ? 'var(--accent-gold)' : 'var(--bg-tertiary)',
              color: activeTab === tab ? '#000' : 'var(--text-secondary)',
              border: 'none', padding: '0.4rem 0.9rem', borderRadius: '6px',
              cursor: 'pointer', fontWeight: 'bold', fontSize: '0.8rem', transition: 'all 0.2s'
            }}>
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* ── Main Content: Chart + Stats (left) | Sales List (right) ── */}
      <div style={{ flex: 1, display: 'flex', gap: '0.75rem', minHeight: 0 }}>

        {/* Left Column */}
        <div style={{ flex: '2 1 0', display: 'flex', flexDirection: 'column', gap: '0.75rem', minWidth: 0, minHeight: 0 }}>

          {/* Bar Chart */}
          <div className="card" style={{ flex: 2, minHeight: 0, padding: '1rem' }}>
            <Bar options={chartOptions} data={chartData} />
          </div>

          {/* 3 Stat Cards in a row */}
          <div style={{ display: 'flex', gap: '0.75rem', flexShrink: 0 }}>
            <div className="card" style={{ flex: 1, padding: '0.9rem 1.2rem', background: 'linear-gradient(135deg,rgba(234,88,12,0.1) 0%,rgba(0,0,0,0) 100%)', border: '1px solid rgba(234,88,12,0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ color: 'var(--primary)', fontWeight: 600, fontSize: '0.8rem' }}>Consumed</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.72rem' }}>{activeTab}</div>
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 'bold' }}>
                {consumedQty} <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{consumedUnit}</span>
              </div>
            </div>
            <div className="card" style={{ flex: 1, padding: '0.9rem 1.2rem', background: 'linear-gradient(135deg,rgba(34,197,94,0.1) 0%,rgba(0,0,0,0) 100%)', border: '1px solid rgba(34,197,94,0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ color: 'rgb(34,197,94)', fontWeight: 600, fontSize: '0.8rem' }}>Units Sold</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.72rem' }}>{activeTab}</div>
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 'bold' }}>
                {totalCategoryUnits} <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Units</span>
              </div>
            </div>
            <div className="card" style={{ flex: 1, padding: '0.9rem 1.2rem', background: 'linear-gradient(135deg,rgba(59,130,246,0.1) 0%,rgba(0,0,0,0) 100%)', border: '1px solid rgba(59,130,246,0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ color: 'rgb(59,130,246)', fontWeight: 600, fontSize: '0.8rem' }}>Revenue</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.72rem' }}>{activeTab}</div>
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                <IndianRupee size={16} style={{ color: 'var(--text-secondary)' }} />
                {totalCategoryAmount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Sales List — ONLY this scrolls */}
        <div className="card" style={{ flex: '1 1 0', display: 'flex', flexDirection: 'column', minWidth: '240px', minHeight: 0, padding: '1rem' }}>
          <h4 style={{ color: 'var(--text-secondary)', marginBottom: '0.75rem', fontSize: '0.9rem', flexShrink: 0 }}>{activeTab} Sales</h4>
          <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.25rem' }}>
            {currentCategoryData.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No {activeTab.toLowerCase()} sales data found.</p>
            ) : (
              currentCategoryData.map((item, idx) => (
                <div key={idx} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '0.65rem 0',
                  borderBottom: idx < currentCategoryData.length - 1 ? '1px solid var(--border)' : 'none'
                }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.88rem', marginBottom: '0.1rem' }}>{item.name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{parseInt(item.total_qty)} units sold</div>
                  </div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 'bold', color: 'var(--primary)', display: 'flex', alignItems: 'center' }}>
                    <IndianRupee size={14} style={{ marginRight: '0.1rem' }} />
                    {parseFloat(item.total_amount).toLocaleString('en-IN')}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
