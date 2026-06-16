import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Inventory from './pages/Inventory';
import Purchases from './pages/Purchases';
import SyncCenter from './pages/SyncCenter';
import Reports from './pages/Reports';
import Login from './pages/Login';
import UserManagement from './pages/UserManagement';

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  if (adminOnly && !user.is_admin) return <Navigate to="/purchases" replace />;
  return children;
};

const AppRoutes = () => {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="inventory" element={<Inventory />} />
        <Route path="purchases" element={<Purchases />} />
        <Route path="sync" element={<ProtectedRoute adminOnly={true}><SyncCenter /></ProtectedRoute>} />
        <Route path="reports/:reportName" element={<ProtectedRoute adminOnly={true}><Reports /></ProtectedRoute>} />
        <Route path="users" element={<ProtectedRoute adminOnly={true}><UserManagement /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
