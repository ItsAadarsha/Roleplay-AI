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

        {sessions.map((session, index) => (
          <div 
            key={session.id} 
            className="session-item"
            onClick={() => handleSessionClick(session, index + 1)}
          >
            <div className="session-label">[{index + 1}]</div>
            <div className="session-info">
              <div>Session ID: {session.id}</div>
              <div className="session-date">
                Created: {new Date(session.created_at).toLocaleString()}
              </div>
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

        {sessions.length === 0 && !loading && (
          <p>No previous sessions. Start a new one!</p>
        )}
      </div>
    </div>
  );
}

export default SessionSelector;
