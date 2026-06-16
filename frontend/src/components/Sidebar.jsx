import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Package, ShoppingCart, RefreshCw, BarChart2, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Sidebar.css';

const Sidebar = () => {
  const { user } = useAuth();
  
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img src="/logo.jpeg" alt="Bier Symphony" className="logo-img" />
        <div className="logo-text">
          <h2>Bier Symphony</h2>
          <p>Inventory Intelligence</p>
        </div>
      </div>
      <nav className="sidebar-nav">
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/inventory" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Package size={20} />
          <span>Inventory</span>
        </NavLink>
        <NavLink to="/purchases" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <ShoppingCart size={20} />
          <span>Purchases</span>
        </NavLink>
        <NavLink to="/sync" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <RefreshCw size={20} />
          <span>Sync Center</span>
        </NavLink>
        
        <div className="nav-section">
          <h4>REPORTS</h4>
          <NavLink to="/reports/stock" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <BarChart2 size={20} />
            <span>Stock Report</span>
          </NavLink>
          <NavLink to="/reports/purchases" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <BarChart2 size={20} />
            <span>Purchase Report</span>
          </NavLink>
          <NavLink to="/reports/consumption" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <BarChart2 size={20} />
            <span>Consumption Report</span>
          </NavLink>
          <NavLink to="/reports/sales-collection" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <BarChart2 size={20} />
            <span>Sales Collection</span>
          </NavLink>
          <NavLink to="/reports/ledger" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <BarChart2 size={20} />
            <span>Inventory Ledger</span>
          </NavLink>
          <NavLink to="/reports/sales-vs-usage" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <BarChart2 size={20} />
            <span>Sales vs Usage</span>
          </NavLink>
        </div>

        {user?.is_admin && (
          <div className="nav-section">
            <h4>ADMIN</h4>
            <NavLink to="/users" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <Users size={20} />
              <span>User Management</span>
            </NavLink>
          </div>
        )}
      </nav>
    </aside>
  );
};

export default Sidebar;
