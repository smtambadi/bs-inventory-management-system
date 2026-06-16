import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import client from '../api/client';
import { Eye, EyeOff, ChevronDown, User, Lock } from 'lucide-react';

const Login = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Username dropdown
  const [users, setUsers] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const dropdownRef = useRef(null);

  // Fetch usernames on mount
  useEffect(() => {
    client.get('users/list/')
      .then(res => setUsers(res.data))
      .catch(() => {}); // Silently ignore if backend not ready
  }, []);

  // Filter users as typing
  useEffect(() => {
    if (username.trim() === '') {
      setFilteredUsers(users);
    } else {
      setFilteredUsers(users.filter(u => u.toLowerCase().includes(username.toLowerCase())));
    }
  }, [username, users]);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleSelectUser = (name) => {
    setUsername(name);
    setShowDropdown(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await client.post('login/', { username, password });
      login(res.data.token, res.data.username, res.data.is_admin);
    } catch {
      setError('Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      height: '100%', background: 'var(--bg-primary)'
    }}>
      <div style={{ width: '100%', maxWidth: '420px', padding: '0 1rem' }}>
        
        {/* Logo card */}
        <div className="card" style={{ padding: '2.5rem 2.5rem 2rem' }}>
          
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <img src="/logo.jpeg" alt="Bier Symphony"
              style={{ width: '72px', height: '72px', borderRadius: '16px', marginBottom: '1rem', objectFit: 'cover', boxShadow: '0 8px 24px rgba(245,166,35,0.2)' }} />
            <h2 style={{ margin: '0 0 0.25rem', fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-gold)' }}>Bier Symphony</h2>
            <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Inventory Intelligence
            </p>
          </div>

          {error && (
            <div style={{
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              color: 'var(--danger)', borderRadius: '8px', padding: '0.75rem 1rem',
              marginBottom: '1.5rem', fontSize: '0.9rem', textAlign: 'center'
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

            {/* ── Username with dropdown ── */}
            <div style={{ position: 'relative' }} ref={dropdownRef}>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 500 }}>
                Username
              </label>
              <div style={{ position: 'relative' }}>
                <User size={16} style={{ position: 'absolute', left: '0.9rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)', pointerEvents: 'none' }} />
                <input
                  className="form-control"
                  style={{ paddingLeft: '2.5rem', paddingRight: '2.5rem' }}
                  value={username}
                  onChange={e => { setUsername(e.target.value); setShowDropdown(true); }}
                  onFocus={() => setShowDropdown(true)}
                  placeholder="Select or type username"
                  autoComplete="off"
                  required
                />
                <button type="button" onClick={() => setShowDropdown(v => !v)}
                  style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: 0, display: 'flex', alignItems: 'center' }}>
                  <ChevronDown size={16} style={{ transition: 'transform 0.2s', transform: showDropdown ? 'rotate(180deg)' : 'rotate(0deg)' }} />
                </button>
              </div>

              {/* Dropdown list */}
              {showDropdown && filteredUsers.length > 0 && (
                <div style={{
                  position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100,
                  background: 'var(--bg-tertiary)', border: '1px solid var(--border)',
                  borderRadius: '10px', marginTop: '4px', overflow: 'hidden',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.4)'
                }}>
                  {filteredUsers.map(name => (
                    <div key={name}
                      onMouseDown={() => handleSelectUser(name)}
                      style={{
                        padding: '0.75rem 1rem', cursor: 'pointer',
                        display: 'flex', alignItems: 'center', gap: '0.75rem',
                        transition: 'background 0.15s',
                        borderBottom: '1px solid var(--border)',
                        color: username === name ? 'var(--accent-gold)' : 'var(--text-primary)',
                        background: username === name ? 'rgba(245,166,35,0.08)' : 'transparent'
                      }}
                      onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                      onMouseLeave={e => e.currentTarget.style.background = username === name ? 'rgba(245,166,35,0.08)' : 'transparent'}
                    >
                      <div style={{
                        width: '30px', height: '30px', borderRadius: '50%',
                        background: 'linear-gradient(135deg,var(--accent-gold),var(--accent-orange))',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontWeight: 700, fontSize: '0.85rem', color: '#000', flexShrink: 0
                      }}>
                        {name[0]?.toUpperCase()}
                      </div>
                      <span style={{ fontWeight: 500 }}>{name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* ── Password with show/hide ── */}
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 500 }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: '0.9rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)', pointerEvents: 'none' }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-control"
                  style={{ paddingLeft: '2.5rem', paddingRight: '2.75rem' }}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                />
                <button type="button" onClick={() => setShowPassword(v => !v)}
                  title={showPassword ? 'Hide password' : 'Show password'}
                  style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '0.2rem', display: 'flex', alignItems: 'center', borderRadius: '4px', transition: 'color 0.2s' }}
                  onMouseEnter={e => e.currentTarget.style.color = 'var(--accent-gold)'}
                  onMouseLeave={e => e.currentTarget.style.color = 'var(--text-secondary)'}
                >
                  {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </div>
            </div>

            {/* ── Submit ── */}
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ width: '100%', padding: '0.85rem', fontSize: '1rem', marginTop: '0.5rem', letterSpacing: '0.02em' }}
            >
              {loading ? (
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
                  <span style={{ width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.7s linear infinite' }} />
                  Authenticating...
                </span>
              ) : 'Sign In'}
            </button>
          </form>
        </div>

        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.78rem', marginTop: '1.5rem' }}>
          Bier Symphony Inventory Intelligence &copy; {new Date().getFullYear()}
        </p>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default Login;
