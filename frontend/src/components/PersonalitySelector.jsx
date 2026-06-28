import React, { useState, useEffect } from 'react';
import { api, getImageUrl } from '../api';
import ConfirmModal from './ConfirmModal.jsx';
import EditModal from './EditModal.jsx';
import Sidebar from './Sidebar.jsx';

function PersonalitySelector({ onPersonaSelected }) {
  const [personalities, setPersonalities] = useState({});
  const [editingPersonaKey, setEditingPersonaKey] = useState(null);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [modalInitialData, setModalInitialData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmTarget, setConfirmTarget] = useState(null);
  const [query, setQuery] = useState('');
  const [activeView, setActiveView] = useState('discover');

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
    } catch (error) {
      console.error('Failed to load personalities:', error);
      setError('Unable to load personalities. Confirm the backend is running.');
      setPersonalities({});
    }
    setLoading(false);
  };

  const handlePersonaClick = (persona) => {
    onPersonaSelected(persona); // pass whole object, not just key
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

  const handleDeletePersona = (e, persona) => {
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

  const filteredList = Object.values(personalities).filter((p) => {
    const search = query.toLowerCase();
    return (
      p.name.toLowerCase().includes(search) ||
      (p.description || '').toLowerCase().includes(search) ||
      p.key.toLowerCase().includes(search)
    );
  });

  return (
    <div className="flex h-screen bg-bg text-text">
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        onCreateClick={() => {
          setEditingPersonaKey(null);
          setModalInitialData(null);
          setEditModalOpen(true);
        }}
      />

      <main className="flex flex-1 flex-col overflow-hidden px-6 pb-6 pt-0">
        <header className="flex flex-wrap items-center justify-between gap-4 py-5">
          <div className=" group max-w-xl flex-1 flex items-center rounded-full border border-border/60 bg-surface/70 px-3 text-sm text-text transition focus-within:border-accent">
            <input
              type="text"
              placeholder="Search personalities…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full px-4 py-2.5 bg-transparent text-sm text-text outline-none transition focus:border-accent"
            />
            <span className="material-symbols-outlined px-3 text-muted transition group-focus-within:text-accent">search</span>
          </div>
          <button
            className="rounded-full bg-accent px-4 py-2 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5"
            onClick={() => {
              setEditingPersonaKey(null);
              setModalInitialData(null);
              setEditModalOpen(true);
            }}
          >
            + Create New
          </button>
        </header>

        {error && <div className="mb-3 rounded-xl border border-rose-400/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div>}
        {toast && <div className="mb-3 rounded-xl border border-emerald-400/40 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">{toast}</div>}

        <section className="flex-1 overflow-y-auto pr-1">
          {loading ? (
            <div className="py-20 text-center text-muted">Loading personalities…</div>
          ) : filteredList.length === 0 ? (
            <div className="rounded-2xl border border-border/60 bg-white/5 px-6 py-16 text-center text-muted">
              <p>No personalities found. Create one to get started.</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <h2 className="mb-4 text-lg font-semibold text-accent">Discover</h2>
                <div className="flex gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {filteredList.map((persona) => (
                    <div
                      key={persona.key}
                      className="group relative flex justify-center items-center cursor-pointer gap-4 rounded-2xl border border-border/60 bg-surface/70 p-4 shadow-lg shadow-black/20 transition hover:-translate-y-1 hover:border-accent/40"
                      onClick={() => handlePersonaClick(persona)}
                    >
                      {/* Square avatar */}
                      <div className="h-24 w-24 shrink-0 overflow-hidden rounded-xl bg-gradient-to-br from-accent2 to-accent">
                        {persona.avatar ? (
                          <img src={getImageUrl(persona.avatar)} alt={persona.name} className="h-full w-full object-cover" />
                        ) : (
                          <div className="flex h-full w-full items-center justify-center text-2xl font-semibold text-slate-950">
                            {persona.name.charAt(0)}
                          </div>
                        )}
                      </div>

                      {/* Info */}
                      <div className="flex flex-1 flex-col justify-between mt-2">
                        <div>
                          <h3 className="text-base font-semibold text-text">{persona.name}</h3>
                          <p className="text-xs text-muted">by @user_{persona.key}</p>
                          <p className="mt-2 text-sm leading-6 text-slate-300 line-clamp-2">{persona.description || 'No description'}</p>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="text-xs text-muted">💬 0 sessions</div>
                          <div className="flex gap-2 opacity-0 transition group-hover:opacity-100">
                            <button
                              className="rounded-lg bg-white/10 px-3 py-1.5 text-sm text-slate-300 hover:bg-emerald-500/15 hover:text-emerald-200"
                              onClick={(e) => handleEditPersona(e, persona)}
                              title="Edit"
                            >
                              <span className="material-symbols-outlined text-base">edit</span>
                            </button>
                            <button
                              className="rounded-lg bg-white/10 px-3 py-1.5 text-sm text-slate-300 hover:bg-rose-500/15 hover:text-rose-200"
                              onClick={(e) => handleDeletePersona(e, persona)}
                              title="Delete"
                            >
                              <span className="material-symbols-outlined text-base">delete</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>
      </main>

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