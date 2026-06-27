import React, { useState, useEffect } from 'react';
import { api, getImageUrl } from '../api';
import ConfirmModal from './ConfirmModal.jsx';
import EditModal from './EditModal.jsx';
import './PersonalitySelector.css';

function PersonalitySelector({ onPersonaSelected }) {
  const [personalities, setPersonalities] = useState({});
  const [selectedKey, setSelectedKey] = useState(null);
  const [editingPersonaKey, setEditingPersonaKey] = useState(null);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [modalInitialData, setModalInitialData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmTarget, setConfirmTarget] = useState(null);
  const [query, setQuery] = useState('');

  useEffect(() => {
    loadPersonalities();
  }, []);

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(''), 3000);
    return () => clearTimeout(timer);
  }, [toast]);

  const loadPersonalities = async () => {
    setError('');
    setLoading(true);
    try {
      const data = await api.getPersonalities();
      setPersonalities(data);
      // Auto-select first if any
      const keys = Object.keys(data);
      if (keys.length > 0 && !selectedKey) {
        setSelectedKey(keys[0]);
      }
    } catch (error) {
      console.error('Failed to load personalities:', error);
      setError('Unable to load personalities. Confirm the backend is running.');
      setPersonalities({});
    }
    setLoading(false);
  };

  const handleSelectPersona = (key) => {
    setSelectedKey(key);
  };

  const handleStartChat = () => {
    if (!selectedKey) return;
    const persona = personalities[selectedKey];
    if (persona) onPersonaSelected(persona);
  };

  const handleSavePersona = async (data) => {
    setLoading(true);
    setError('');
    setToast('');
    try {
      if (editingPersonaKey) {
        await api.updatePersonality(editingPersonaKey, data);
      } else {
        await api.createPersonality(data);
      }
      await loadPersonalities();
      setEditModalOpen(false);
      setEditingPersonaKey(null);
      setModalInitialData(null);
      setToast('Persona saved successfully');
    } catch (error) {
      console.error('Failed to save personality:', error);
      setError(`Failed to save personality: ${error.message}`);
      setToast(`Failed to save: ${error.message}`);
    }
    setLoading(false);
  };

  const handleEditPersona = (e, persona) => {
    e.stopPropagation();
    setEditingPersonaKey(persona.key);
    setModalInitialData(persona);
    setEditModalOpen(true);
  };

  const handleDeletePersona = async (e, persona) => {
    e.stopPropagation();
    setConfirmTarget(persona);
    setConfirmOpen(true);
  };

  const doDeleteConfirmed = async () => {
    if (!confirmTarget) return;
    setConfirmOpen(false);
    setLoading(true);
    setError('');
    setToast('');
    try {
      await api.deletePersonality(confirmTarget.key);
      setToast(`Deleted ${confirmTarget.name}`);
      await loadPersonalities();
      // If deleted was selected, clear selection
      if (selectedKey === confirmTarget.key) {
        const keys = Object.keys(personalities);
        setSelectedKey(keys.length > 0 ? keys[0] : null);
      }
    } catch (error) {
      console.error('Failed to delete personality:', error);
      setError(`Failed to delete personality: ${error.message}`);
      setToast(`Delete failed: ${error.message}`);
    }
    setConfirmTarget(null);
    setLoading(false);
  };

  const handleCancelEdit = () => {
    setEditModalOpen(false);
    setEditingPersonaKey(null);
    setModalInitialData(null);
  };

  const filteredKeys = Object.keys(personalities).filter((key) => {
    const p = personalities[key];
    const search = query.toLowerCase();
    return (
      p.name.toLowerCase().includes(search) ||
      key.toLowerCase().includes(search) ||
      (p.description || '').toLowerCase().includes(search)
    );
  });

  const selectedPersona = selectedKey ? personalities[selectedKey] : null;

  return (
    <div className="dashboard">
      {/* Error / Toast */}
      {error && <div className="dashboard-error">{error}</div>}
      {toast && <div className="dashboard-toast">{toast}</div>}

      <div className="dashboard-layout">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <h2>Personalities</h2>
            <button
              className="btn-icon-only"
              onClick={() => {
                setEditingPersonaKey(null);
                setModalInitialData(null);
                setEditModalOpen(true);
              }}
              disabled={loading}
              title="Create new"
            >
              +
            </button>
          </div>
          <div className="sidebar-search">
            <input
              type="text"
              placeholder="Search…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="sidebar-list">
            {loading && <p className="loading-text">Loading…</p>}
            {!loading && filteredKeys.length === 0 && (
              <p className="empty-text">No personalities found.</p>
            )}
            {filteredKeys.map((key) => {
              const p = personalities[key];
              const isActive = selectedKey === key;
              return (
                <div
                  key={key}
                  className={`sidebar-item ${isActive ? 'active' : ''}`}
                  onClick={() => handleSelectPersona(key)}
                >
                  <div className="sidebar-avatar">
                    {p.avatar ? (
                      <img src={getImageUrl(p.avatar)} alt={p.name} />
                    ) : (
                      <span>{p.name.charAt(0)}</span>
                    )}
                  </div>
                  <div className="sidebar-info">
                    <div className="sidebar-name">{p.name}</div>
                    <div className="sidebar-key">#{key}</div>
                  </div>
                  <div className="sidebar-actions">
                    <button
                      className="btn-icon-small"
                      onClick={(e) => handleEditPersona(e, p)}
                      title="Edit"
                    >
                      ✎
                    </button>
                    <button
                      className="btn-icon-small btn-delete"
                      onClick={(e) => handleDeletePersona(e, p)}
                      title="Delete"
                    >
                      🗑
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </aside>

        {/* Main content */}
        <main className="main-content">
          {selectedPersona ? (
            <div className="persona-detail">
              <div className="detail-header">
                <div className="detail-avatar-large">
                  {selectedPersona.avatar ? (
                    <img src={getImageUrl(selectedPersona.avatar)} alt={selectedPersona.name} />
                  ) : (
                    <span>{selectedPersona.name.charAt(0)}</span>
                  )}
                </div>
                <div className="detail-info">
                  <h1>{selectedPersona.name}</h1>
                  <p className="detail-description">{selectedPersona.description || 'No description'}</p>
                  <div className="detail-meta">
                    <span>Key: #{selectedPersona.key}</span>
                  </div>
                </div>
              </div>

              <div className="detail-actions">
                <button className="btn-primary btn-start" onClick={handleStartChat}>
                  ▶ Start Chat
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => {
                    setEditingPersonaKey(selectedPersona.key);
                    setModalInitialData(selectedPersona);
                    setEditModalOpen(true);
                  }}
                >
                  Edit
                </button>
              </div>

              {/* Future: list recent sessions here */}
              <div className="detail-sessions">
                <h3>Recent Sessions</h3>
                <p className="hint">Sessions will appear here after you chat.</p>
              </div>
            </div>
          ) : (
            <div className="empty-detail">
              <h2>Select a personality</h2>
              <p>Choose from the sidebar to see details and start chatting.</p>
            </div>
          )}
        </main>
      </div>

      <EditModal
        open={editModalOpen}
        initialData={modalInitialData}
        onSave={handleSavePersona}
        onCancel={handleCancelEdit}
        saving={loading}
      />
      <ConfirmModal
        open={confirmOpen}
        title="Delete Persona"
        message={confirmTarget ? `Delete persona '${confirmTarget.name}'? This cannot be undone.` : ''}
        onConfirm={doDeleteConfirmed}
        onCancel={() => setConfirmOpen(false)}
      />
    </div>
  );
}

export default PersonalitySelector;