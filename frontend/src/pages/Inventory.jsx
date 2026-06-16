import React, { useState, useEffect } from 'react';
import client from '../api/client';

const Inventory = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get('inventory/')
      .then(res => {
        setItems(res.data);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <div className="flex justify-between items-center" style={{ marginBottom: '2rem' }}>
        <h2>Inventory Items</h2>
        <button className="btn btn-primary">Add Item</button>
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Item Name</th>
              <th>Unit</th>
              <th>Reorder Level</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="5">Loading...</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan="5">No items found.</td></tr>
            ) : (
              items.map(item => (
                <tr key={item.InventoryItemId}>
                  <td>#{item.InventoryItemId}</td>
                  <td style={{ fontWeight: '500', color: 'var(--text-primary)' }}>{item.ItemName}</td>
                  <td>{item.Unit}</td>
                  <td>{parseFloat(item.ReorderLevel)}</td>
                  <td>
                    <span className={`badge ${item.IsActive ? 'badge-success' : 'badge-danger'}`}>
                      {item.IsActive ? 'Active' : 'Inactive'}
                    </span>
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

export default Inventory;
