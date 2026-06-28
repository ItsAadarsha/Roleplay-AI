import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, getImageUrl } from '../api';

function Sidebar({ activeView, onViewChange, onCreateClick }) {
  const [width, setWidth] = useState(224);
  const [recentSessions, setRecentSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.getRecentSessions()
      .then(data => setRecentSessions(data.sessions))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = width;

    const onMouseMove = (e) => {
      const newWidth = Math.min(400, Math.max(160, startWidth + e.clientX - startX));
      setWidth(newWidth);
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  }, [width]);

  const items = [
    { key: 'create', label: 'Create', icon: <span className="material-symbols-outlined">add</span> },
    { key: 'discover', label: 'Discover', icon: <span className="material-symbols-outlined">explore</span> },
    { key: 'feed', label: 'Feed', icon: <span className="material-symbols-outlined">rss_feed</span> },
  ];

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  return (
    <aside
      style={{ width: `${width}px` }}
      className="relative flex shrink-0 flex-col border-r border-border/70 bg-surface/80 px-0 py-5 backdrop-blur-xl"
    >
      <div
        onClick={() => navigate('/')}
        className="px-10 pb-6 text-xl text-center font-semibold tracking-tight text-text cursor-pointer hover:text-accent transition"
      >
        <span className="bg-accent bg-clip-text text-transparent">SARP</span>
      </div>

      <nav className="flex flex-col gap-1 px-3">
        {items.map((item) => {
          const isActive = activeView === item.key;
          return (
            <button
              key={item.key}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition ${isActive ? 'bg-accent/10 text-accent' : 'text-muted hover:bg-white/5 hover:text-white'}`}
              onClick={item.key === 'create' ? onCreateClick : () => onViewChange(item.key)}
            >
              <span className="flex h-5 w-5 items-center justify-center">{item.icon}</span>
              <span className="leading-none">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Recent Sessions */}
      <div className="mt-4 flex flex-col gap-1 px-3 overflow-y-auto flex-1">
        <p className="px-3 py-1 text-xs font-semibold uppercase tracking-widest text-muted/60">
          Recent
        </p>

        {loading ? (
          <p className="px-3 text-xs text-muted/50">Loading...</p>
        ) : recentSessions.length === 0 ? (
          <p className="px-3 text-xs text-muted/50">No recent sessions.</p>
        ) : (
          recentSessions.map((session) => (
            <button
                key={session.id}
                onClick={() => navigate(`/chat/${session.id}`)}
                className="flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-left transition hover:bg-white/5"
            >
                {/* Avatar */}
                <div className="h-8 w-8 shrink-0 overflow-hidden rounded-full bg-gradient-to-br from-accent2 to-accent">
                    {session.persona_avatar ? (
                        <img src={getImageUrl(session.persona_avatar)} alt={session.persona_name} className="h-full w-full object-cover" />
                    ) : (
                        <div className="flex h-full w-full items-center justify-center text-sm font-semibold text-slate-950">
                            {session.persona_name?.charAt(0)}
                        </div>
                    )}
                </div>

                {/* Text */}
                <div className="flex min-w-0 flex-1 flex-col gap-0.5">
                    <div className="flex items-center justify-between gap-2">
                        <span className="truncate text-sm font-medium text-text">
                            {session.persona_name}
                        </span>
                        <span className="shrink-0 text-xs text-muted/50">
                            {formatDate(session.updated_at)}
                        </span>
                    </div>
                    <span className="truncate text-xs text-muted/60">
                        {session.last_user_message ?? 'No messages yet'}
                    </span>
                </div>
            </button>
        ))
        )}
      </div>

      {/* Drag handle */}
      <div
        onMouseDown={handleMouseDown}
        className="absolute right-0 top-0 h-full w-1 cursor-col-resize hover:bg-accent/40 transition-colors"
      />
    </aside>
  );
}

export default Sidebar;