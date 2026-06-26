const API_BASE = import.meta.env.VITE_API_URL || '';

async function handleResponse(res) {
  const text = await res.text();
  let payload = null;

  try {
    payload = text ? JSON.parse(text) : null;
  } catch (err) {
    payload = null;
  }

  if (!res.ok) {
    const message = payload?.detail || payload?.message || text || res.statusText;
    throw new Error(message || 'Request failed');
  }

  return payload;
}

export const api = {
  // Personalities
  async getPersonalities() {
    const res = await fetch(`${API_BASE}/personalities`);
    return handleResponse(res);
  },

  async createPersonality(data) {
    const res = await fetch(`${API_BASE}/personalities`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return handleResponse(res);
  },

  async pickPersonality(choice) {
    const res = await fetch(`${API_BASE}/personalities/pick`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ choice })
    });
    return res.json();
  },

  // Sessions
  async getSessions(personaName) {
    const res = await fetch(`${API_BASE}/sessions/${encodeURIComponent(personaName)}`);
    return res.json();
  },

  async pickSession(personaName, index) {
    const res = await fetch(`${API_BASE}/sessions/pick`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        persona_name: personaName, 
        index 
      })
    });
    return res.json();
  },

  async loadSession(personaKey, session) {
    const res = await fetch(`${API_BASE}/sessions/load`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        persona_key: personaKey, 
        session 
      })
    });
    return res.json();
  },

  async saveSession(personaKey, fullMessages, sessionId) {
    const res = await fetch(`${API_BASE}/sessions/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        persona_key: personaKey,
        full_messages: fullMessages,
        session_id: sessionId
      })
    });
    return res.json();
  },

  // Chat
  async sendMessage(personaKey, messages, fullMessages, sessionId, userInput) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        persona_key: personaKey,
        messages,
        full_messages: fullMessages,
        session_id: sessionId,
        user_input: userInput
      })
    });
    return res.json();
  }
};
