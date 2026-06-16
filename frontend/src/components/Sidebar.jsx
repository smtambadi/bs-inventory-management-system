import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Package, ShoppingCart, RefreshCw, BarChart2, Users, Boxes, Receipt, TrendingDown, Wallet, BookOpen, Scale } from 'lucide-react';
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
        {/* Dashboard — visible to all users */}
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end title="Dashboard">
          <LayoutDashboard size={20} style={{ minWidth: '20px' }} />
          <span className="nav-label">Dashboard</span>
        </NavLink>

        {/* All users */}
        <NavLink to="/inventory" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Inventory">
          <Package size={20} style={{ minWidth: '20px' }} />
          <span className="nav-label">Inventory</span>
        </NavLink>
        <NavLink to="/purchases" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Purchases">
          <ShoppingCart size={20} style={{ minWidth: '20px' }} />
          <span className="nav-label">Purchases</span>
        </NavLink>

        {/* Admin-only: Sync Center, Reports, Admin */}
        {user?.is_admin && (
          <>
            <NavLink to="/sync" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Sync Center">
              <RefreshCw size={20} style={{ minWidth: '20px' }} />
              <span className="nav-label">Sync Center</span>
            </NavLink>

            <div className="nav-section">
              <h4 className="nav-group-title">REPORTS</h4>
              <NavLink to="/reports/stock" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Stock Report">
                <Boxes size={20} style={{ minWidth: '20px' }} />
                <span className="nav-label">Stock Report</span>
              </NavLink>
              <NavLink to="/reports/purchases" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Purchase Report">
                <Receipt size={20} style={{ minWidth: '20px' }} />
                <span className="nav-label">Purchase Report</span>
              </NavLink>
              <NavLink to="/reports/consumption" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Consumption Report">
                <TrendingDown size={20} style={{ minWidth: '20px' }} />
                <span className="nav-label">Consumption Report</span>
              </NavLink>
              <NavLink to="/reports/sales-collection" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Sales Collection">
                <Wallet size={20} style={{ minWidth: '20px' }} />
                <span className="nav-label">Sales Collection</span>
              </NavLink>
              <NavLink to="/reports/ledger" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Inventory Ledger">
                <BookOpen size={20} style={{ minWidth: '20px' }} />
                <span className="nav-label">Inventory Ledger</span>
              </NavLink>
              <NavLink to="/reports/sales-vs-usage" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="Sales vs Usage">
                <Scale size={20} style={{ minWidth: '20px' }} />
                <span className="nav-label">Sales vs Usage</span>
              </NavLink>
            </div>

            <div className="nav-section">
              <h4 className="nav-group-title">ADMIN</h4>
              <NavLink to="/users" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`} title="User Management">
                <Users size={20} style={{ minWidth: '20px' }} />
                <span className="nav-label">User Management</span>
              </NavLink>
            </div>
          </>
        )}
      </nav>
    </aside>
  );
};

export default Sidebar;
