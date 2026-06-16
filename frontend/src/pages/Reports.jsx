import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import client from '../api/client';
import { Download, Filter } from 'lucide-react';

const Reports = () => {
  const { reportName } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const [startDate, setStartDate] = useState(searchParams.get('start') || '');
  const [endDate, setEndDate] = useState(searchParams.get('end') || '');
  
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReport = () => {
    setLoading(true);
    setError(null);
    
    let url = `reports/${reportName}/`;
    const params = new URLSearchParams();
    if (startDate) params.append('start', startDate);
    if (endDate) params.append('end', endDate);
    if (params.toString()) url += `?${params.toString()}`;

    client.get(url)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.toString());
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchReport();
  }, [reportName, searchParams]);

  const handleApplyFilter = () => {
    setSearchParams({ start: startDate, end: endDate });
  };

  const getReportTitle = () => {
    return reportName.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') + ' Report';
  };

  const handleExport = () => {
    if (data.length === 0) return;
    
    const headers = Object.keys(data[0]);
    const csvRows = [];
    csvRows.push(headers.join(','));
    
    for (const row of data) {
      const values = headers.map(header => {
        const val = row[header] === null ? '' : String(row[header]);
        return `"${val.replace(/"/g, '""')}"`;
      });
      csvRows.push(values.join(','));
    }
    
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', `${reportName}.csv`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  // Calculate totals for numeric columns
  const getTotals = () => {
    if (data.length === 0) return null;
    const totals = {};
    const firstRow = data[0];
    
    Object.keys(firstRow).forEach(key => {
      // Only sum if every value in this column is a number
      const isNumeric = data.every(row => typeof row[key] === 'number' || !isNaN(parseFloat(row[key])));
      
      if (isNumeric && key !== 'Date' && key !== 'PurchaseId' && key !== 'InventoryItemId') {
        totals[key] = data.reduce((sum, row) => sum + (parseFloat(row[key]) || 0), 0);
      } else {
        totals[key] = null;
      }
    });
    return totals;
  };

  const totals = getTotals();

  return (
    <div>
      <div className="flex justify-between items-center" style={{ marginBottom: '2rem' }}>
        <h2>{getReportTitle()}</h2>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <input 
              type="date" 
              className="form-control" 
              value={startDate} 
              onChange={e => setStartDate(e.target.value)} 
              placeholder="Start Date"
            />
            <span style={{ color: 'var(--text-secondary)' }}>to</span>
            <input 
              type="date" 
              className="form-control" 
              value={endDate} 
              onChange={e => setEndDate(e.target.value)} 
              placeholder="End Date"
            />
            <button className="btn btn-secondary" onClick={handleApplyFilter} style={{ padding: '0.6rem 1rem' }}>
              <Filter size={16} /> Filter
            </button>
          </div>
          <button className="btn btn-secondary" onClick={handleExport} disabled={data.length === 0}>
            <Download size={16} /> Export CSV
          </button>
        </div>
      </div>

      <div className="card" style={{ overflowX: 'auto' }}>
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading report data...</div>
        ) : error ? (
          <div style={{ padding: '2rem', color: 'var(--danger)' }}>Error loading report: {error}</div>
        ) : data.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>No data found for this report in the selected date range.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                {Object.keys(data[0]).map(key => (
                  <th key={key}>{key.replace(/([A-Z])/g, ' $1').trim()}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => (
                <tr key={i}>
                  {Object.keys(row).map(key => (
                    <td key={`${i}-${key}`}>
                      {typeof row[key] === 'number' 
                        ? (row[key] % 1 === 0 ? row[key] : parseFloat(row[key]).toFixed(2)) 
                        : row[key] === null ? '-' : String(row[key])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
            {totals && (
              <tfoot>
                <tr style={{ backgroundColor: 'rgba(245, 166, 35, 0.05)', fontWeight: 'bold' }}>
                  {Object.keys(totals).map((key, i) => (
                    <td key={`total-${key}`}>
                      {i === 0 ? 'TOTAL' : totals[key] !== null ? (totals[key] % 1 === 0 ? totals[key] : totals[key].toFixed(2)) : ''}
                    </td>
                  ))}
                </tr>
              </tfoot>
            )}
          </table>
        )}
      </div>
    </div>
  );
};

export default Reports;
