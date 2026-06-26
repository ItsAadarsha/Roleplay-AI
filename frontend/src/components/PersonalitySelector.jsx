import React, { useState, useEffect } from 'react';
import { api } from '../api';
import './PersonalitySelector.css';

function PersonalitySelector({ onPersonaSelected }) {
  const [personalities, setPersonalities] = useState({});
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    system: '',
    scenario: '',
    opening_prompt: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPersonalities();
  }, []);

  const loadPersonalities = async () => {
    setLoading(true);
    try {
      const data = await api.getPersonalities();
      setPersonalities(data);
    } catch (error) {
      console.error('Failed to load personalities:', error);
    }
    setLoading(false);
  };

  const handlePersonaClick = (persona) => {
    onPersonaSelected(persona);
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const newPersona = await api.createPersonality(formData);
      await loadPersonalities();
      setShowCreateForm(false);
      setFormData({ name: '', system: '', scenario: '', opening_prompt: '' });
      onPersonaSelected(newPersona);
    } catch (error) {
      console.error('Failed to create personality:', error);
      alert(`Failed to create personality: ${error.message}`);
    }
    setLoading(false);
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const personalityList = Object.values(personalities);

  return (
    <div className="personality-selector">
      <h1>SELECT PERSONALITY</h1>

      {loading && <p>Loading...</p>}

      {!showCreateForm && (
        <>
          <div className="personality-list">
            {personalityList.length === 0 && !loading && (
              <p>No personalities found. Create one to get started.</p>
            )}

            {personalityList.map((persona) => (
              <div 
                key={persona.key} 
                className="personality-item"
                onClick={() => handlePersonaClick(persona)}
              >
                <div className="persona-key">[{persona.key}]</div>
                <div className="persona-name">{persona.name}</div>
              </div>
            ))}
          </div>

          <button 
            className="btn-create"
            onClick={() => setShowCreateForm(true)}
          >
            + CREATE NEW PERSONALITY
          </button>
        </>
      )}

      {showCreateForm && (
        <form className="create-form" onSubmit={handleCreateSubmit}>
          <div className="form-group">
            <label>Name:</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label>System Prompt:</label>
            <textarea
              name="system"
              value={formData.system}
              onChange={handleInputChange}
              rows="4"
              required
            />
          </div>

          <div className="form-group">
            <label>Scenario:</label>
            <textarea
              name="scenario"
              value={formData.scenario}
              onChange={handleInputChange}
              rows="4"
              required
            />
          </div>

          <div className="form-group">
            <label>Opening Prompt:</label>
            <textarea
              name="opening_prompt"
              value={formData.opening_prompt}
              onChange={handleInputChange}
              rows="3"
              required
            />
          </div>

          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create'}
            </button>
            <button 
              type="button" 
              onClick={() => setShowCreateForm(false)}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default PersonalitySelector;
