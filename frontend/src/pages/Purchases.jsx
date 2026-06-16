import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { Plus, X, ChevronDown, ChevronUp, Trash2, Edit, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Purchases = () => {
  const { user } = useAuth();
  const [purchases, setPurchases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [expandedPurchase, setExpandedPurchase] = useState(null);
  const [purchaseDetails, setPurchaseDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  // Modal States
  const [deleteConfirm, setDeleteConfirm] = useState(null); 
  const [editItemModal, setEditItemModal] = useState(null);
  const [newItemModal, setNewItemModal] = useState(null);
  const [alertMsg, setAlertMsg] = useState(null);

  // Form State
  const [supplier, setSupplier] = useState('');
  const [invoice, setInvoice] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [items, setItems] = useState([{ id: '', quantity: '', unit_price: '' }]);
  const [inventoryItems, setInventoryItems] = useState([]);

  useEffect(() => {
    fetchPurchases();
    fetchInventory();
  }, []);

  const fetchPurchases = async () => {
    try {
      const res = await client.get('purchases/');
      setPurchases(res.data);
      setLoading(false);
    } catch (err) {
      setAlertMsg(err.message || 'Failed to fetch purchases');
    }
  };

  const fetchInventory = async () => {
    try {
      const res = await client.get('inventory/');
      setInventoryItems(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const toggleExpand = async (id) => {
    if (expandedPurchase === id) {
      setExpandedPurchase(null);
      setPurchaseDetails(null);
    } else {
      setExpandedPurchase(id);
      setDetailsLoading(true);
      try {
        const res = await client.get(`purchases/${id}/`);
        setPurchaseDetails(res.data);
      } catch (err) {
        setAlertMsg('Error fetching details');
      } finally {
        setDetailsLoading(false);
      }
    }
  };

  const triggerDeletePurchase = (id, e) => {
    e.stopPropagation();
    setDeleteConfirm({
      type: 'purchase',
      id: id,
      message: 'WARNING: Deleting this purchase will reverse the stock addition. Are you sure you want to completely delete this purchase?'
    });
  };

  const triggerDeleteItem = (itemId) => {
    setDeleteConfirm({
      type: 'item',
      id: itemId,
      message: 'Are you sure you want to delete this line item and reverse its stock?'
    });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm) return;
    try {
      if (deleteConfirm.type === 'purchase') {
        await client.delete(`purchases/${deleteConfirm.id}/`);
        if (expandedPurchase === deleteConfirm.id) setExpandedPurchase(null);
      } else {
        await client.delete(`purchase-items/${deleteConfirm.id}/`);
        const res = await client.get(`purchases/${expandedPurchase}/`);
        setPurchaseDetails(res.data);
      }
      fetchPurchases();
    } catch (err) {
      setAlertMsg(err.response?.data?.error || 'Error deleting record');
    } finally {
      setDeleteConfirm(null);
    }
  };

  const triggerEditItem = (item) => {
    setEditItemModal({ ...item });
  };

  const confirmEditItem = async (e) => {
    e.preventDefault();
    if (isNaN(editItemModal.quantity) || isNaN(editItemModal.unit_price)) {
      setAlertMsg('Invalid numbers provided.');
      return;
    }
    try {
      await client.put(`purchase-items/${editItemModal.id}/`, {
        quantity: editItemModal.quantity,
        unit_price: editItemModal.unit_price
      });
      const res = await client.get(`purchases/${expandedPurchase}/`);
      setPurchaseDetails(res.data);
      fetchPurchases();
    } catch (err) {
      setAlertMsg(err.response?.data?.error || 'Error updating item');
    } finally {
      setEditItemModal(null);
    }
  };

  const confirmNewItem = async (e) => {
    e.preventDefault();
    if (isNaN(newItemModal.quantity) || isNaN(newItemModal.unit_price)) {
      setAlertMsg('Invalid numbers provided.');
      return;
    }
    try {
      await client.post(`purchases/${newItemModal.purchase_id}/`, {
        inventory_item_id: newItemModal.inventory_item_id,
        quantity: newItemModal.quantity,
        unit_price: newItemModal.unit_price
      });
      const res = await client.get(`purchases/${expandedPurchase}/`);
      setPurchaseDetails(res.data);
      fetchPurchases();
    } catch (err) {
      setAlertMsg(err.response?.data?.error || 'Error adding item');
    } finally {
      setNewItemModal(null);
    }
  };

  const handleAddItem = () => {
    setItems([...items, { id: '', quantity: '', unit_price: '' }]);
  };

  const handleRemoveItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...items];
    newItems[index][field] = value;
    setItems(newItems);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await client.post('purchases/', {
        supplier_name: supplier,
        invoice_number: invoice,
        purchase_date: date,
        items: items.map(item => ({
          ...item,
          id: parseInt(item.id),
          quantity: parseFloat(item.quantity),
          unit_price: parseFloat(item.unit_price)
        }))
      });
      setShowForm(false);
      setSupplier('');
      setInvoice('');
      setItems([{ id: '', quantity: '', unit_price: '' }]);
      fetchPurchases();
      setAlertMsg('Purchase recorded successfully!');
    } catch (err) {
      setAlertMsg('Error recording purchase: ' + (err.response?.data?.error || err.message));
    }
  };

  // Modals Styles
  const overlayStyle = {
    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.75)',
    display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
  };
  const modalBoxStyle = {
    backgroundColor: 'var(--card-bg)', padding: '2rem', borderRadius: '8px',
    width: '100%', maxWidth: '400px', boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
  };

  return (
    <div>
      {/* Alert / Notification Modal */}
      {alertMsg && (
        <div style={overlayStyle}>
          <div style={modalBoxStyle} className="animate-fade-in">
            <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Notice</h3>
            <p style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>{alertMsg}</p>
            <div className="flex justify-end">
              <button className="btn btn-primary" onClick={() => setAlertMsg(null)}>OK</button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div style={overlayStyle}>
          <div style={modalBoxStyle} className="animate-fade-in">
            <div className="flex items-center gap-3" style={{ marginBottom: '1rem', color: 'var(--danger)' }}>
              <AlertTriangle size={24} />
              <h3 style={{ margin: 0 }}>Confirm Deletion</h3>
            </div>
            <p style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>{deleteConfirm.message}</p>
            <div className="flex justify-end gap-3">
              <button className="btn" style={{ background: 'var(--bg-lighter)' }} onClick={() => setDeleteConfirm(null)}>Cancel</button>
              <button className="btn" style={{ background: 'var(--danger)', color: 'white' }} onClick={confirmDelete}>Confirm Delete</button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Item Modal */}
      {editItemModal && (
        <div style={overlayStyle}>
          <div style={modalBoxStyle} className="animate-fade-in">
            <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Edit {editItemModal.item_name}</h3>
            <form onSubmit={confirmEditItem}>
              <div className="form-group">
                <label>Quantity</label>
                <input 
                  required 
                  type="number" 
                  step="0.0001" 
                  className="form-control" 
                  value={editItemModal.quantity} 
                  onChange={e => setEditItemModal({...editItemModal, quantity: e.target.value})} 
                />
              </div>
              <div className="form-group">
                <label>Unit Price (₹)</label>
                <input 
                  required 
                  type="number" 
                  step="0.01" 
                  className="form-control" 
                  value={editItemModal.unit_price} 
                  onChange={e => setEditItemModal({...editItemModal, unit_price: e.target.value})} 
                />
              </div>
              <div className="flex justify-end gap-3 mt-4">
                <button type="button" className="btn" style={{ background: 'var(--bg-lighter)' }} onClick={() => setEditItemModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add New Item Modal */}
      {newItemModal && (
        <div style={overlayStyle}>
          <div style={modalBoxStyle} className="animate-fade-in">
            <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Add Line Item to Purchase</h3>
            <form onSubmit={confirmNewItem}>
              <div className="form-group">
                <label>Inventory Item</label>
                <select 
                  required 
                  className="form-control" 
                  value={newItemModal.inventory_item_id} 
                  onChange={e => setNewItemModal({...newItemModal, inventory_item_id: e.target.value})}
                >
                  <option value="">Select Item...</option>
                  {inventoryItems.map(inv => (
                    <option key={inv.InventoryItemId} value={inv.InventoryItemId}>{inv.ItemName} ({inv.Unit})</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input 
                  required 
                  type="number" 
                  step="0.0001" 
                  className="form-control" 
                  value={newItemModal.quantity} 
                  onChange={e => setNewItemModal({...newItemModal, quantity: e.target.value})} 
                />
              </div>
              <div className="form-group">
                <label>Unit Price (₹)</label>
                <input 
                  required 
                  type="number" 
                  step="0.01" 
                  className="form-control" 
                  value={newItemModal.unit_price} 
                  onChange={e => setNewItemModal({...newItemModal, unit_price: e.target.value})} 
                />
              </div>
              <div className="flex justify-end gap-3 mt-4">
                <button type="button" className="btn" style={{ background: 'var(--bg-lighter)' }} onClick={() => setNewItemModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Add Item</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center" style={{ marginBottom: '2rem' }}>
        <h2>Purchases</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Record Purchase'}
        </button>
      </div>

      {showForm && (
        <div className="card animate-fade-in" style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>New Purchase Entry</h3>
          <form onSubmit={handleSubmit}>
            <div className="flex gap-4">
              <div className="form-group" style={{ flex: 1 }}>
                <label>Supplier Name</label>
                <input required className="form-control" value={supplier} onChange={e => setSupplier(e.target.value)} />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label>Invoice Number</label>
                <input required className="form-control" value={invoice} onChange={e => setInvoice(e.target.value)} />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label>Date</label>
                <input required type="date" className="form-control" value={date} onChange={e => setDate(e.target.value)} />
              </div>
            </div>

            <h4 style={{ marginTop: '1rem', marginBottom: '1rem' }}>Line Items</h4>
            {items.map((item, index) => (
              <div key={index} className="flex gap-4 items-center" style={{ marginBottom: '1rem' }}>
                <div className="form-group" style={{ flex: 2, marginBottom: 0 }}>
                  <select required className="form-control" value={item.id} onChange={e => handleItemChange(index, 'id', e.target.value)}>
                    <option value="">Select Item...</option>
                    {inventoryItems.map(inv => (
                      <option key={inv.InventoryItemId} value={inv.InventoryItemId}>{inv.ItemName} ({inv.Unit})</option>
                    ))}
                  </select>
                </div>
                <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                  <input required type="number" step="0.0001" placeholder="Qty" className="form-control" value={item.quantity} onChange={e => handleItemChange(index, 'quantity', e.target.value)} />
                </div>
                <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                  <input required type="number" step="0.01" placeholder="Unit Price" className="form-control" value={item.unit_price} onChange={e => handleItemChange(index, 'unit_price', e.target.value)} />
                </div>
                <div style={{ flex: 1, fontWeight: 'bold' }}>
                  Total: ₹{((parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)).toFixed(2)}
                </div>
                {items.length > 1 && (
                  <button type="button" onClick={() => handleRemoveItem(index)} style={{ background: 'none', color: 'var(--danger)' }}>
                    <X size={20} />
                  </button>
                )}
              </div>
            ))}
            
            <div className="flex justify-between items-center mt-4">
              <button type="button" className="btn btn-secondary" onClick={handleAddItem}>
                <Plus size={16} /> Add Line Item
              </button>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                Grand Total: ₹{items.reduce((sum, item) => sum + ((parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)), 0).toFixed(2)}
              </div>
            </div>
            
            <div className="flex gap-4 mt-8">
              <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Save Purchase</button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '40px' }}></th>
              <th>Date</th>
              <th>Supplier</th>
              <th>Invoice #</th>
              <th>Total Amount</th>
              {user?.is_admin && <th style={{ width: '80px', textAlign: 'right' }}>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={user?.is_admin ? "6" : "5"}>Loading...</td></tr>
            ) : purchases.length === 0 ? (
              <tr><td colSpan={user?.is_admin ? "6" : "5"}>No purchases found.</td></tr>
            ) : (
              purchases.map(p => (
                <React.Fragment key={p.PurchaseId}>
                  <tr 
                    style={{ cursor: 'pointer', backgroundColor: expandedPurchase === p.PurchaseId ? 'var(--bg-lighter)' : 'transparent' }}
                    onClick={() => toggleExpand(p.PurchaseId)}
                  >
                    <td>
                      {expandedPurchase === p.PurchaseId ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </td>
                    <td>{new Date(p.PurchaseDate).toLocaleDateString()}</td>
                    <td>{p.SupplierName}</td>
                    <td>{p.InvoiceNumber}</td>
                    <td style={{ fontWeight: 'bold' }}>₹{parseFloat(p.TotalAmount).toFixed(2)}</td>
                    {user?.is_admin && (
                      <td style={{ textAlign: 'right' }}>
                        <button 
                          onClick={(e) => triggerDeletePurchase(p.PurchaseId, e)}
                          style={{ background: 'none', color: 'var(--danger)', padding: '0.2rem' }}
                          title="Delete Entire Purchase"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    )}
                  </tr>
                  
                  {expandedPurchase === p.PurchaseId && (
                    <tr>
                      <td colSpan={user?.is_admin ? "6" : "5"} style={{ padding: 0, borderBottom: '1px solid var(--border)' }}>
                        <div style={{ padding: '1rem 2rem', backgroundColor: 'var(--bg-dark)' }}>
                          <h4 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Purchase Line Items</h4>
                          {detailsLoading ? (
                            <div>Loading items...</div>
                          ) : purchaseDetails?.items ? (
                            <>
                              <table className="data-table" style={{ backgroundColor: 'var(--card-bg)' }}>
                                <thead>
                                <tr>
                                  <th>Item</th>
                                  <th>Quantity</th>
                                  <th>Unit Price</th>
                                  <th>Total</th>
                                  {user?.is_admin && <th style={{ textAlign: 'right' }}>Actions</th>}
                                </tr>
                              </thead>
                              <tbody>
                                {purchaseDetails.items.map(item => (
                                  <tr key={item.id}>
                                    <td>{item.item_name}</td>
                                    <td>{parseFloat(item.quantity).toFixed(2)}</td>
                                    <td>₹{parseFloat(item.unit_price).toFixed(2)}</td>
                                    <td>₹{parseFloat(item.total_price).toFixed(2)}</td>
                                    {user?.is_admin && (
                                      <td style={{ textAlign: 'right' }}>
                                        <button 
                                          onClick={() => triggerEditItem(item)}
                                          style={{ background: 'none', color: 'var(--primary)', padding: '0.2rem', marginRight: '0.5rem' }}
                                          title="Edit Item"
                                        >
                                          <Edit size={16} />
                                        </button>
                                        <button 
                                          onClick={() => triggerDeleteItem(item.id)}
                                          style={{ background: 'none', color: 'var(--danger)', padding: '0.2rem' }}
                                          title="Delete Item"
                                        >
                                          <Trash2 size={16} />
                                        </button>
                                      </td>
                                    )}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                            {user?.is_admin && (
                              <div className="flex justify-end mt-4">
                                <button className="btn btn-secondary" onClick={() => setNewItemModal({ purchase_id: p.PurchaseId, inventory_item_id: '', quantity: '', unit_price: '' })}>
                                  <Plus size={16} style={{ marginRight: '0.5rem' }} /> Add Line Item
                                </button>
                              </div>
                            )}
                          </>
                          ) : (
                            <div>No details available</div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Purchases;
