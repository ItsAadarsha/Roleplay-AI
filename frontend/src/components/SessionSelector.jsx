import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api, getImageUrl } from '../api';

function SessionSelector({ persona, onSessionSelected, onBack }) {
  const { personaKey } = useParams();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (!persona?.key) return;
    loadSessions();
  }, [persona, personaKey]);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const data = await api.getSessions(persona.key);
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
    setLoading(false);
  };

  const handleSelectSession = (session) => onSessionSelected(session);
  const handleNewSession = () => onSessionSelected(null);

  const handleDeleteSession = async (e, session) => {
    e.stopPropagation();
    if (!window.confirm(`Delete session ${session.id}?`)) return;
    try {
      await api.deleteSession(persona.key, session.id);
      await loadSessions();
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const getDateGroup = (dateStr) => {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    if (date.toDateString() === today.toDateString()) return 'Today';
    if (date.toDateString() === yesterday.toDateString()) return 'Yesterday';
    return 'Older';
  };

  const filteredSessions = sessions.filter((session) => {
    const q = searchQuery.toLowerCase();
    return (
      session.id.toString().includes(q) ||
      new Date(session.updated_at).toLocaleString().toLowerCase().includes(q)
    );
  });

  const grouped = filteredSessions.reduce((acc, session) => {
    const group = getDateGroup(session.updated_at || session.created_at);
    if (!acc[group]) acc[group] = [];
    acc[group].push(session);
    return acc;
  }, {});

  const sortedGroups = ['Today', 'Yesterday', 'Older'].filter((g) => grouped[g]);

  const getPreview = (session) => {
    if (session.messages && session.messages.length > 0) {
      const firstUserMsg = session.messages.find(m => m.role === 'user');
      if (firstUserMsg) return firstUserMsg.content.slice(0, 60) + '...';
      return session.messages[0].content.slice(0, 60) + '...';
    }
    return 'No messages yet';
  };

  return (
    <div className="flex h-screen bg-bg text-text">
      <aside className="w-56 shrink-0 border-r border-border/70 bg-surface/80 p-5 backdrop-blur-xl flex flex-col">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-accent2 to-accent text-lg font-semibold text-slate-950">
            {persona.avatar ? (
              <img src={getImageUrl(persona.avatar)} alt={persona.name} className="h-full w-full object-cover" />
            ) : (
              <span>{persona.name.charAt(0)}</span>
            )}
          </div>
          <div>
            <h3 className="text-base font-semibold text-text">{persona.name}</h3>
            <p className="text-xs text-muted">#{persona.key}</p>
          </div>
        </div>
        <button
          className="mb-4 flex items-center gap-2 rounded-xl border border-border/60 bg-white/5 px-3 py-2 text-left text-sm text-muted transition hover:text-white"
          onClick={onBack}
        >
          <span className="material-symbols-outlined text-base">keyboard_backspace</span>
          Back to personalities
        </button>
        <div className="mt-auto rounded-xl border border-border/60 bg-white/5 px-3 py-3 text-sm text-muted text-center">
          <span className="material-symbols-outlined text-base align-middle mr-1">chat</span>
          {sessions.length} sessions
        </div>
      </aside>

      <main className="flex flex-1 flex-col overflow-hidden px-6 py-6">
        <header className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl font-semibold text-text">
            Your Sessions
            <span className="ml-2 text-sm font-normal text-muted">({sessions.length})</span>
          </h1>
          <div className="flex items-center gap-3 flex-1 max-w-sm">
            <div className="group flex flex-1 items-center rounded-full border border-border/60 bg-surface/70 px-3 py-2 text-sm text-text transition focus-within:border-accent">
              <span className="material-symbols-outlined ml-0.5 text-muted transition group-focus-within:text-accent">
                search
              </span>
              <input
                type="text"
                placeholder="Search sessions…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-transparent px-4 py-5.5 text-sm text-text outline-none placeholder:text-muted"
              />
            </div>
            <button
              className="flex items-center gap-1.5 rounded-full bg-gradient-to-r from-accent to-accent2 px-4 py-2 text-sm font-semibold text-slate-950 shadow-lg shadow-emerald-500/20 transition hover:-translate-y-0.5 whitespace-nowrap"
              onClick={handleNewSession}
            >
              <span className="material-symbols-outlined text-base">add</span>
              New Chat
            </button>
          </div>
        </header>

        {loading && <p className="py-4 text-center text-muted">Loading sessions…</p>}

        <div className="flex-1 overflow-y-auto pr-1">
          {sortedGroups.length === 0 && !loading && (
            <div className="flex h-full flex-col items-center justify-center rounded-2xl border border-border/60 bg-gradient-to-b from-surface/40 to-transparent px-6 py-16 text-center">
              <span className="material-symbols-outlined text-6xl text-muted/50">chat</span>
              <h2 className="mt-4 text-2xl font-semibold text-text">No sessions yet</h2>
              <p className="mt-2 max-w-sm text-sm text-muted">
                Start your first chat with <strong>{persona.name}</strong> and go <b>WILD!</b>
              </p>
              <button
                className="mt-6 flex items-center gap-2 rounded-full bg-gradient-to-r from-accent to-accent2 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-accent/30 transition hover:scale-105"
                onClick={handleNewSession}
              >
                <span className="material-symbols-outlined text-base">add</span>
                Start New Chat
              </button>
            </div>
          )}

          {sortedGroups.map((groupName) => (
            <div key={groupName} className="mb-6">
              <div className="mb-3 flex items-center gap-2 border-b border-border/60 pb-2">
                <span className="text-[11px] font-semibold uppercase tracking-[0.2em] text-muted">{groupName}</span>
                <span className="text-xs text-muted">({grouped[groupName].length})</span>
              </div>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {grouped[groupName].map((session) => (
                  <div
                    key={session.id}
                    className="group relative cursor-pointer rounded-2xl border border-border/60 bg-surface/70 p-4 shadow-lg shadow-black/20 transition hover:-translate-y-1 hover:border-accent/40 hover:shadow-accent/10"
                    onClick={() => handleSelectSession(session)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-xl text-accent">chat</span>
                        <span className="font-medium text-text">Session #{session.id}</span>
                      </div>
                      <button
                        className="rounded-lg p-1 text-muted transition hover:bg-rose-500/10 hover:text-rose-200"
                        onClick={(e) => handleDeleteSession(e, session)}
                        title="Delete session"
                      >
                        <span className="material-symbols-outlined text-base">delete</span>
                      </button>
                    </div>
                    <div className="mt-2 text-sm text-muted line-clamp-2">
                      {getPreview(session)}
                    </div>
                    <div className="mt-3 text-xs text-muted">
                      {new Date(session.updated_at).toLocaleString()}
                    </div>
                    <div className="mt-2 flex justify-end opacity-0 transition group-hover:opacity-100">
                      <span className="flex items-center gap-0.5 text-xs text-accent">
                        Open
                        <span className="material-symbols-outlined text-sm">arrow_forward</span>
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default SessionSelector;