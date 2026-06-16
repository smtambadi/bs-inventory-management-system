import React, { createContext, useContext, useState, useEffect } from 'react';
import client from '../api/client';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    const is_admin = localStorage.getItem('is_admin') === 'true';

    if (token && username) {
      setUser({ token, username, is_admin });
      // Configure client immediately
      client.defaults.headers.common['Authorization'] = `Token ${token}`;
    }
    setLoading(false);
  }, []);

  const login = (token, username, is_admin) => {
    localStorage.setItem('token', token);
    localStorage.setItem('username', username);
    localStorage.setItem('is_admin', is_admin);
    setUser({ token, username, is_admin });
    client.defaults.headers.common['Authorization'] = `Token ${token}`;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('is_admin');
    setUser(null);
    delete client.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
