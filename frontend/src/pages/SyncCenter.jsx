import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { RefreshCw, Play, CheckCircle, XCircle } from 'lucide-react';

const SyncCenter = () => {
  const [syncing, setSyncing] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const handleRunSync = async () => {
    setSyncing(true);
    setResult(null);
    try {
      const res = await client.post('sync/run/');
      setResult({ type: 'sync', data: res.data });
    } catch (err) {
      setResult({ type: 'sync', error: err.toString() });
    } finally {
      setSyncing(false);
    }
  };

  const handleProcessDeltas = async () => {
    setProcessing(true);
    setResult(null);
    try {
      const res = await client.post('sync/process/');
      setResult({ type: 'process', data: res.data });
    } catch (err) {
      setResult({ type: 'process', error: err.toString() });
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '2rem' }}>Sync Center</h2>

      <div className="flex gap-6">
        <div className="card" style={{ flex: 1 }}>
          <div className="flex items-center gap-4" style={{ marginBottom: '1.5rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'rgba(245, 166, 35, 0.1)', borderRadius: '50%', color: 'var(--accent-gold)' }}>
              <RefreshCw size={32} className={syncing ? 'spin' : ''} />
            </div>
            <div>
              <h3 style={{ margin: 0 }}>Detect POS Changes</h3>
              <p style={{ color: 'var(--text-secondary)', margin: '0.25rem 0 0 0', fontSize: '0.9rem' }}>
                Reads from VANGROTIPARKDB and detects new sales or returns.
              </p>
            </div>
          </div>
          <button 
            className="btn btn-primary" 
            onClick={handleRunSync}
            disabled={syncing || processing}
            style={{ width: '100%' }}
          >
            {syncing ? 'Syncing...' : 'Run Sync Now'}
          </button>
        </div>

        <div className="card" style={{ flex: 1 }}>
          <div className="flex items-center gap-4" style={{ marginBottom: '1.5rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'rgba(45, 212, 168, 0.1)', borderRadius: '50%', color: 'var(--success)' }}>
              <Play size={32} />
            </div>
            <div>
              <h3 style={{ margin: 0 }}>Process Deltas</h3>
              <p style={{ color: 'var(--text-secondary)', margin: '0.25rem 0 0 0', fontSize: '0.9rem' }}>
                Converts detected changes into inventory transactions.
              </p>
            </div>
          </div>
          <button 
            className="btn btn-secondary" 
            onClick={handleProcessDeltas}
            disabled={syncing || processing}
            style={{ width: '100%' }}
          >
            {processing ? 'Processing...' : 'Process Deltas'}
          </button>
        </div>
      </div>

      {result && (
        <div className="card animate-fade-in" style={{ marginTop: '2rem' }}>
          <div className="flex items-center gap-2" style={{ marginBottom: '1rem' }}>
            {result.data?.success ? (
              <CheckCircle color="var(--success)" />
            ) : (
              <XCircle color="var(--danger)" />
            )}
            <h3 style={{ margin: 0 }}>
              {result.type === 'sync' ? 'Sync Result' : 'Process Result'}
            </h3>
          </div>
          
          <pre style={{ 
            backgroundColor: 'rgba(0,0,0,0.2)', 
            padding: '1rem', 
            borderRadius: '8px',
            overflowX: 'auto',
            color: result.data?.success ? 'var(--text-primary)' : 'var(--danger)',
            fontSize: '0.85rem'
          }}>
            {result.error || result.data?.output || result.data?.error}
          </pre>
        </div>
      )}

      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
        .spin { animation: spin 1s linear infinite; }
      `}</style>
    </div>
  );
};

export default SyncCenter;
