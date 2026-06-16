import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { AlertCircle, IndianRupee } from 'lucide-react';
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

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [data, setData] = useState({ stock: [], item_sales: [] });
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
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchDashboardData();
  }, [dateFilterType, startDate, endDate]);

  if (loading) return <div>Loading dashboard...</div>;

  const currentCategoryData = data.item_sales?.filter(item => item.category === activeTab) || [];
  const totalCategoryUnits = currentCategoryData.reduce((sum, item) => sum + parseInt(item.total_qty), 0);
  const totalCategoryAmount = currentCategoryData.reduce((sum, item) => sum + parseFloat(item.total_amount), 0);

  const chartData = {
    labels: currentCategoryData.map(item => item.name),
    datasets: [
      {
        label: 'Total Collection (₹)',
        data: currentCategoryData.map(item => item.total_amount),
        backgroundColor: 'rgba(234, 88, 12, 0.8)',
        borderColor: '#ea580c',
        borderWidth: 1,
        borderRadius: 4,
      }
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context) => `₹${context.raw.toLocaleString()}`
        }
      }
    },
    scales: {
      y: {
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      },
      x: {
        ticks: { color: '#9ca3af' },
        grid: { display: false }
      }
    }
  };

  const tabs = ['CHICKEN', 'MUTTON', 'BOTI', 'RICE', 'EGG'];

  return (
    <div>
      <div className="flex justify-between items-center" style={{ marginBottom: '2rem' }}>
        <h2>Dashboard Overview</h2>
      </div>

      <div className="flex gap-6" style={{ flexWrap: 'wrap', marginBottom: '3rem' }}>
        {data.stock.map(item => (
          <div key={item.id} className="card" style={{ flex: '1 1 220px', position: 'relative', overflow: 'hidden' }}>
            {item.status === 'LOW' && (
              <div style={{ position: 'absolute', top: '1rem', right: '1rem', color: 'var(--warning)' }}>
                <AlertCircle size={20} />
              </div>
            )}
            <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
              {item.name}
            </h3>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: item.status === 'LOW' ? 'var(--warning)' : 'var(--success)' }}>
              {parseFloat(item.current_stock).toFixed(2)} <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>{item.unit}</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
              Reorder Level: {item.reorder_level}
            </div>
            {item.status === 'LOW' && (
              <div style={{ position: 'absolute', bottom: 0, left: 0, width: '100%', height: '4px', backgroundColor: 'var(--warning)' }}></div>
            )}
          </div>
        ))}
      </div>

      <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h3 style={{ fontSize: '1.2rem', margin: 0 }}>Sales Breakdown</h3>
        
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', background: 'var(--bg-dark)', padding: '0.5rem', borderRadius: '8px' }}>
          <select 
            className="form-control" 
            style={{ width: 'auto', marginBottom: 0 }}
            value={dateFilterType}
            onChange={(e) => setDateFilterType(e.target.value)}
          >
            <option value="today">Today</option>
            <option value="yesterday">Yesterday</option>
            <option value="custom">Custom Date(s)</option>
          </select>
          
          {dateFilterType === 'custom' && (
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <input 
                type="date" 
                className="form-control" 
                style={{ width: 'auto', marginBottom: 0 }} 
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
              <span style={{ color: 'var(--text-secondary)' }}>to</span>
              <input 
                type="date" 
                className="form-control" 
                style={{ width: 'auto', marginBottom: 0 }} 
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          )}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {tabs.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                background: activeTab === tab ? 'var(--primary)' : 'var(--bg-lighter)',
                color: activeTab === tab ? 'white' : 'var(--text-secondary)',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 'bold',
                transition: 'background 0.2s'
              }}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-6" style={{ flexWrap: 'wrap', marginBottom: '2rem' }}>
        <div style={{ flex: '2 1 600px', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="card" style={{ height: '400px' }}>
            <Bar options={chartOptions} data={chartData} />
          </div>
          
          <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1.5rem 2rem', background: 'linear-gradient(135deg, rgba(234, 88, 12, 0.1) 0%, rgba(0,0,0,0) 100%)', border: '1px solid rgba(234, 88, 12, 0.2)' }}>
            <div>
              <h4 style={{ color: 'var(--primary)', marginBottom: '0.2rem', fontSize: '1.1rem' }}>Total {activeTab} Consumed</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>Calculated from items sold in selected range</p>
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
              {data.consumption?.find(c => c.ingredient_name.toUpperCase() === activeTab) 
                ? parseFloat(data.consumption.find(c => c.ingredient_name.toUpperCase() === activeTab).consumed_qty).toFixed(2) 
                : '0.00'} 
              <span style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginLeft: '0.5rem' }}>KG</span>
            </div>
          </div>
          
          <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1.5rem 2rem', background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(0,0,0,0) 100%)', border: '1px solid rgba(34, 197, 94, 0.2)' }}>
            <div>
              <h4 style={{ color: 'rgb(34, 197, 94)', marginBottom: '0.2rem', fontSize: '1.1rem' }}>Total {activeTab} Units Sold</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>Total count of items in this category</p>
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
              {totalCategoryUnits} 
              <span style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginLeft: '0.5rem' }}>Units</span>
            </div>
          </div>

          <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1.5rem 2rem', background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(0,0,0,0) 100%)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
            <div>
              <h4 style={{ color: 'rgb(59, 130, 246)', marginBottom: '0.2rem', fontSize: '1.1rem' }}>Total {activeTab} Revenue</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>Total sales amount for this category</p>
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
              <span style={{ fontSize: '1.8rem', color: 'var(--text-secondary)', marginRight: '0.2rem' }}>₹</span>
              {totalCategoryAmount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          </div>
        </div>
        
        <div className="card" style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h4 style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>{activeTab} Sales</h4>
          <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem' }}>
            {currentCategoryData.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>No {activeTab.toLowerCase()} sales data found.</p>
            ) : (
              currentCategoryData.map((item, idx) => (
                <div key={idx} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '1rem 0',
                  borderBottom: idx < currentCategoryData.length - 1 ? '1px solid var(--border)' : 'none'
                }}>
                  <div>
                    <div style={{ fontWeight: 'bold', fontSize: '1rem', marginBottom: '0.2rem' }}>{item.name}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{parseInt(item.total_qty)} units sold</div>
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--primary)', display: 'flex', alignItems: 'center' }}>
                    <IndianRupee size={16} style={{ marginRight: '0.1rem' }}/>
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
