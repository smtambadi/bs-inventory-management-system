import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Trash2, UserPlus, Key } from 'lucide-react';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  
  const { user: currentUser } = useAuth();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await client.get('users/');
      setUsers(res.data);
      setLoading(false);
    } catch (err) {
      alert('Error fetching users');
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await client.post('users/', { username, password, is_admin: isAdmin });
      alert('User created successfully');
      setShowForm(false);
      setUsername('');
      setPassword('');
      setIsAdmin(false);
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.error || 'Error creating user');
    }
  };

  const handleDeleteUser = async (id) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await client.delete(`users/${id}/`);
        alert('User deleted');
        fetchUsers();
      } catch (err) {
        alert(err.response?.data?.error || 'Error deleting user');
      }
    }
  };

  const handleResetPassword = async (id) => {
    const newPassword = window.prompt('Enter new password for this user:');
    if (newPassword) {
      try {
        await client.put(`users/${id}/`, { password: newPassword });
        alert('Password updated successfully');
      } catch (err) {
        alert(err.response?.data?.error || 'Error updating password');
      }
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center" style={{ marginBottom: '2rem' }}>
        <h2>User Management</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          <UserPlus size={18} style={{ marginRight: '0.5rem' }} />
          {showForm ? 'Cancel' : 'New User'}
        </button>
      </div>

      {showForm && (
        <div className="card animate-fade-in" style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Create New User</h3>
          <form onSubmit={handleCreateUser}>
            <div className="flex gap-4">
              <div className="form-group" style={{ flex: 1 }}>
                <label>Username</label>
                <input required className="form-control" value={username} onChange={e => setUsername(e.target.value)} />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label>Password</label>
                <input required type="password" className="form-control" value={password} onChange={e => setPassword(e.target.value)} />
              </div>
              <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end', paddingBottom: '0.8rem' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input type="checkbox" checked={isAdmin} onChange={e => setIsAdmin(e.target.checked)} style={{ width: '20px', height: '20px' }} />
                  <span>Admin Privilege</span>
                </label>
              </div>
            </div>
            <button type="submit" className="btn btn-primary mt-4">Create User</button>
          </form>
        </div>
      )}

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="4">Loading...</td></tr>
            ) : (
              users.map(u => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.username} {currentUser.username === u.username && '(You)'}</td>
                  <td>
                    <span className={`status-badge ${u.is_staff ? 'status-ok' : ''}`}>
                      {u.is_staff ? 'Admin' : 'Cashier'}
                    </span>
                  </td>
                  <td>
                    <div className="flex gap-2">
                      <button 
                        className="btn btn-secondary" 
                        title="Reset Password"
                        onClick={() => handleResetPassword(u.id)}
                      >
                        <Key size={16} />
                      </button>
                      {currentUser.username !== u.username && (
                        <button 
                          className="btn btn-secondary" 
                          style={{ color: 'var(--danger)' }} 
                          title="Delete User"
                          onClick={() => handleDeleteUser(u.id)}
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UserManagement;
