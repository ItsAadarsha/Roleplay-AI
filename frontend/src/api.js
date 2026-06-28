const API_BASE = import.meta.env.VITE_API_URL || '';
const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function getImageUrl(path) {
  if (!path) return null;
  // If path is already a full URL, return as-is
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  // If path starts with /, construct backend URL
  if (path.startsWith('/')) return `${BACKEND_URL}${path}`;
  // Otherwise, assume it's a relative path
  return `${BACKEND_URL}/${path}`;
}

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
    const formData = new FormData();
    formData.append('name', data.name);
    if (data.description) formData.append('description', data.description);
    formData.append('system', data.system);
    formData.append('scenario', data.scenario);
    formData.append('opening_prompt', data.opening_prompt);
    if (data.avatar instanceof File) {
      formData.append('avatar', data.avatar);
    }
    
    const res = await fetch(`${API_BASE}/personalities`, {
      method: 'POST',
      body: formData
    });
    return handleResponse(res);
  },

  async pickPersonality(choice) {
    const res = await fetch(`${API_BASE}/personalities/pick`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ choice })
    });
    return handleResponse(res);
  },

  async updatePersonality(personaKey, data) {
    const formData = new FormData();
    formData.append('name', data.name);
    if (data.description) formData.append('description', data.description);
    formData.append('system', data.system);
    formData.append('scenario', data.scenario);
    formData.append('opening_prompt', data.opening_prompt);
    if (data.avatar instanceof File) {
      formData.append('avatar', data.avatar);
    }
    
    const res = await fetch(`${API_BASE}/personalities/${encodeURIComponent(personaKey)}`, {
      method: 'PUT',
      body: formData
    });
    return handleResponse(res);
  },

  async deletePersonality(personaKey) {
    const res = await fetch(`${API_BASE}/personalities/${encodeURIComponent(personaKey)}`, {
      method: 'DELETE'
    });
    return handleResponse(res);
  },

  // Sessions
  async getRecentSessions() {
    const res = await fetch(`${API_BASE}/sessions/recent`);
    return handleResponse(res);
  },

  async getSessions(personaName, personaId) {
    const qs = personaId ? `?persona_id=${encodeURIComponent(personaId)}` : '';
    const res = await fetch(`${API_BASE}/sessions/${encodeURIComponent(personaName)}${qs}`);
    return handleResponse(res);
  },

  async pickSession(personaName, personaId, index) {
    const res = await fetch(`${API_BASE}/sessions/pick`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        persona_name: personaName,
        persona_id: personaId,
        index 
      })
    });
    return handleResponse(res);
  },

  async loadSession(personaKey, personaName, personaId, session) {
    const res = await fetch(`${API_BASE}/sessions/load`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        persona_key: personaKey,
        persona_name: personaName,
        persona_id: personaId,
        session 
      })
    });
    return handleResponse(res);
  },

 async saveSession(personaKey, messages, context, sessionId) {
    const res = await fetch(`${API_BASE}/sessions/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            persona_key: personaKey,
            messages,
            context,
            session_id: sessionId
        })
    });
    return handleResponse(res);
},

  async deleteSession(personaName, personaId, sessionId) {
    const res = await fetch(`${API_BASE}/sessions/${encodeURIComponent(personaName)}/${sessionId}`, {
      method: 'DELETE'
    });
    return handleResponse(res);
  },

  // Chat
  async sendMessage(personaKey, messages, context, sessionId, userInput) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        persona_key: personaKey,
        messages,
        context: context,
        session_id: sessionId,
        user_input: userInput
      })
    });
    return handleResponse(res);
  }
};
