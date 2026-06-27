import React, { useState, useEffect } from 'react';
import { api } from '../api';
import './SessionSelector.css';

function SessionSelector({ persona, onSessionSelected, onBack }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSessions();
  }, [persona]);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const data = await api.getSessions(persona.name);
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
    setLoading(false);
  };

  const handleSessionClick = async (session, index) => {
    onSessionSelected(session);
  };

  const handleNewSession = () => {
    onSessionSelected(null);
  };

  const handleDeleteSession = async (e, session) => {
    e.stopPropagation();
    if (!window.confirm(`Delete session ${session.id}?`)) {
      return;
    }

    try {
      await api.deleteSession(persona.name, session.id);
      await loadSessions();
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  // NEW: group sessions by date (Today, Yesterday, Older)
  const getDateGroup = (dateStr) => {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) return 'Today';
    if (date.toDateString() === yesterday.toDateString()) return 'Yesterday';
    return 'Older';
  };

  const grouped = sessions.reduce((acc, session) => {
    const group = getDateGroup(session.updated_at || session.created_at);
    if (!acc[group]) acc[group] = [];
    acc[group].push(session);
    return acc;
  }, {});

  const sortedGroups = ['Today', 'Yesterday', 'Older'].filter(g => grouped[g]);

  return (
    <div className="session-selector">
      <button className="btn-back" onClick={onBack}>
        ← BACK TO PERSONALITIES
      </button>

      <h1>SELECT SESSION</h1>
      <h2>Personality: {persona.name}</h2>

      {loading && <p>Loading sessions...</p>}

      <div className="session-list">
        <div 
          className="session-item new-session"
          onClick={handleNewSession}
        >
          <div className="session-label">[NEW]</div>
          <div className="session-info">Start a new conversation</div>
        </div>

        {sortedGroups.map((groupName) => (
          <div key={groupName}>
            <div className="session-group-header">{groupName}</div>
            {grouped[groupName].map((session, index) => (
              <div 
                key={session.id} 
                className="session-item"
                onClick={() => handleSessionClick(session, index + 1)}
              >
                <div className="session-label">[{index + 1}]</div>
                <div className="session-info">
                  <div className="session-id">Session ID: {session.id}</div>
                  <div className="session-date">
                    Updated: {new Date(session.updated_at).toLocaleString()}
                  </div>
                </div>
                <button
                  type="button"
                  className="session-action-btn"
                  onClick={(e) => handleDeleteSession(e, session)}
                  title={`Delete session ${session.id}`}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        ))}

        {sessions.length === 0 && !loading && (
          <p>No previous sessions. Start a new one!</p>
        )}
      </div>
    </div>
  );
}

export default SessionSelector;