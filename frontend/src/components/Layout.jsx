import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { useAuth } from '../context/AuthContext';
import { LogOut, Menu } from 'lucide-react';
import './Layout.css';

const Layout = () => {
  const { user, logout } = useAuth();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="layout-container">
      <Sidebar isCollapsed={isSidebarCollapsed} />
      <main className={`main-content ${isSidebarCollapsed ? 'collapsed' : ''}`}>
        <header className="main-header">
          <div className="header-left" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button 
              onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
              style={{ background: 'none', border: 'none', color: 'var(--text-primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '0.5rem', borderRadius: '8px' }}
              className="hover-bg"
            >
              <Menu size={24} />
            </button>
            <h1>Inventory Intelligence</h1>
          </div>
          <div className="header-right">
            <div className="user-profile" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div className="avatar" style={{ background: 'var(--primary)', color: 'white', width: '35px', height: '35px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                {user?.username?.[0]?.toUpperCase()}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontWeight: 'bold', textTransform: 'capitalize' }}>{user?.username}</span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {user?.is_admin ? 'Admin' : 'Cashier'}
                </span>
              </div>
              <button 
                onClick={logout} 
                className="btn btn-secondary" 
                style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', marginLeft: '1rem' }}
                title="Logout"
              >
                <LogOut size={16} />
              </button>
            </div>
          </div>
        </header>
        <div className="page-content animate-fade-in">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
