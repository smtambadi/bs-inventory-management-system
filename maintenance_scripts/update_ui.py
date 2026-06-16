import os

# 1. Update Layout.jsx
layout_jsx = """import React, { useState } from 'react';
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
"""

# 2. Update Layout.css
layout_css = """.layout-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  flex: 1;
  margin-left: 260px; /* Width of sidebar */
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow-y: auto;
  transition: margin-left 0.3s ease;
}

.main-content.collapsed {
  margin-left: 80px;
}

.main-header {
  height: 70px;
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-left h1 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.hover-bg:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-gold), var(--accent-orange));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.page-content {
  padding: 2rem;
  flex: 1;
}
"""

# 3. Update Sidebar.jsx
sidebar_jsx = """import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Package, ShoppingCart, RefreshCw, BarChart2, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Sidebar.css';

const Sidebar = ({ isCollapsed }) => {
  const { user } = useAuth();
  
  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-logo">
        <img src="/logo.jpeg" alt="Bier Symphony" className="logo-img" />
        <div className="logo-text">
          <h2>Bier Symphony</h2>
          <p>Inventory Intelligence</p>
        </div>
      </div>
      <nav className="sidebar-nav custom-scrollbar">
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end title="Dashboard">
          <LayoutDashboard size={20} style={{ minWidth: '20px' }} />
          <span className="nav-label">Dashboard</span>
        </NavLink>
        <NavLink to="/inventory" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Inventory">
          <Package size={20} style={{ minWidth: '20px' }} />
          <span className="nav-label">Inventory</span>
        </NavLink>
        <NavLink to="/purchases" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Purchases">
          <ShoppingCart size={20} style={{ minWidth: '20px' }} />
          <span className="nav-label">Purchases</span>
        </NavLink>
        <NavLink to="/sync" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Sync Center">
          <RefreshCw size={20} style={{ minWidth: '20px' }} />
          <span className="nav-label">Sync Center</span>
        </NavLink>
        
        <div className="nav-section">
          <h4 className="nav-group-title">REPORTS</h4>
          <NavLink to="/reports/stock" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Stock Report">
            <BarChart2 size={20} style={{ minWidth: '20px' }} />
            <span className="nav-label">Stock Report</span>
          </NavLink>
          <NavLink to="/reports/purchases" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Purchase Report">
            <BarChart2 size={20} style={{ minWidth: '20px' }} />
            <span className="nav-label">Purchase Report</span>
          </NavLink>
          <NavLink to="/reports/consumption" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Consumption Report">
            <BarChart2 size={20} style={{ minWidth: '20px' }} />
            <span className="nav-label">Consumption Report</span>
          </NavLink>
          <NavLink to="/reports/sales-collection" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Sales Collection">
            <BarChart2 size={20} style={{ minWidth: '20px' }} />
            <span className="nav-label">Sales Collection</span>
          </NavLink>
          <NavLink to="/reports/ledger" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Inventory Ledger">
            <BarChart2 size={20} style={{ minWidth: '20px' }} />
            <span className="nav-label">Inventory Ledger</span>
          </NavLink>
          <NavLink to="/reports/sales-vs-usage" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Sales vs Usage">
            <BarChart2 size={20} style={{ minWidth: '20px' }} />
            <span className="nav-label">Sales vs Usage</span>
          </NavLink>
        </div>

        {user?.is_admin && (
          <div className="nav-section">
            <h4 className="nav-group-title">ADMIN</h4>
            <NavLink to="/users" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="User Management">
              <Users size={20} style={{ minWidth: '20px' }} />
              <span className="nav-label">User Management</span>
            </NavLink>
          </div>
        )}
      </nav>
    </aside>
  );
};

export default Sidebar;
"""

# 4. Update Sidebar.css
sidebar_css = """.sidebar {
  width: 260px;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border);
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
  z-index: 20;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-logo {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid var(--border);
  height: 70px;
  box-sizing: border-box;
}

.logo-img {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.logo-text {
  transition: opacity 0.2s ease, width 0.2s ease;
  white-space: nowrap;
  opacity: 1;
  width: auto;
}

.sidebar.collapsed .logo-text {
  opacity: 0;
  width: 0;
  overflow: hidden;
}

.logo-text h2 {
  font-size: 1.1rem;
  color: var(--accent-gold);
  margin: 0;
  font-weight: 700;
}

.logo-text p {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sidebar-nav {
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  overflow-y: auto;
  overflow-x: hidden;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  color: var(--text-primary);
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.sidebar.collapsed .nav-item {
  padding: 0.75rem;
  justify-content: center;
}

.nav-label {
  transition: opacity 0.2s ease, width 0.2s ease;
  opacity: 1;
}

.sidebar.collapsed .nav-label {
  opacity: 0;
  width: 0;
  display: none;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--accent-gold);
}

.nav-item.active {
  background-color: rgba(245, 166, 35, 0.1);
  color: var(--accent-gold);
  border-left: 3px solid var(--accent-gold);
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.nav-section {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-group-title {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
  padding-left: 1rem;
  font-weight: 600;
  white-space: nowrap;
  transition: opacity 0.2s ease;
}

.sidebar.collapsed .nav-group-title {
  opacity: 0;
  height: 0;
  margin: 0;
  overflow: hidden;
}
"""

with open(r'd:\BS\frontend\src\components\Layout.jsx', 'w', encoding='utf-8') as f:
    f.write(layout_jsx)

with open(r'd:\BS\frontend\src\components\Layout.css', 'w', encoding='utf-8') as f:
    f.write(layout_css)

with open(r'd:\BS\frontend\src\components\Sidebar.jsx', 'w', encoding='utf-8') as f:
    f.write(sidebar_jsx)

with open(r'd:\BS\frontend\src\components\Sidebar.css', 'w', encoding='utf-8') as f:
    f.write(sidebar_css)

print("Files updated successfully!")
