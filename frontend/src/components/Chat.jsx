import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import './Chat.css';

function Chat({ persona, session, onBack }) {
  const [messages, setMessages] = useState([]);
  const [fullMessages, setFullMessages] = useState([]);
  const [sessionId, setSessionId] = useState(session?.id || null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    initializeChat();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeChat = async () => {
    setInitializing(true);
    try {
      const data = await api.loadSession(persona.key, session);
      setMessages(data.messages || []);
      setFullMessages(data.full_messages || []);
      setSessionId(session?.id || null);
    } catch (error) {
      console.error('Failed to load session:', error);
      alert('Failed to load chat session');
    }
    setInitializing(false);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userInput = input.trim();
    setInput('');
    setLoading(true);

    try {
      const data = await api.sendMessage(
        persona.key,
        messages,
        fullMessages,
        sessionId,
        userInput
      );
      setMessages(data.messages);
      setFullMessages(data.full_messages);
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message');
    }

    setLoading(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleSaveSession = async () => {
    if (fullMessages.length === 0) {
      alert('No messages to save');
      return;
    }
    setLoading(true);
    try {
      const data = await api.saveSession(persona.key, fullMessages, sessionId);
      setSessionId(data.session_id);
      alert('Session saved successfully!');
    } catch (error) {
      console.error('Failed to save session:', error);
      alert('Failed to save session');
    }
    setLoading(false);
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  if (initializing) {
    return (
      <div className="chat">
        <p>Loading chat...</p>
      </div>
    );
  }

  return (
    <div className="chat">
      <div className="chat-header">
        <button className="btn-back" onClick={onBack}>
          ← Back
        </button>
        <div className="chat-info">
          <span className="persona-name">{persona.name}</span>
          <span className="session-id">Session #{sessionId || 'New'}</span>
        </div>
        <button
          className="btn-save"
          onClick={handleSaveSession}
          disabled={loading || fullMessages.length === 0}
        >
          Save
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((msg, index) => {
          if (msg.role === 'system') return null;
          const roleClass = msg.role === 'user' ? 'user' : 'assistant';
          const roleLabel = msg.role === 'user' ? 'You' : persona.name;

          return (
            <div key={index} className={`message ${roleClass}`}>
              <div className="message-header">
                <span className="message-role">{roleLabel}</span>
              </div>
              <div className="message-content">{msg.content}</div>
            </div>
          );
        })}

        {loading && (
          <div className="message assistant">
            <div className="message-header">
              <span className="message-role">{persona.name}</span>
            </div>
            <div className="message-content typing-indicator">…</div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message… (Shift+Enter for new line)"
          disabled={loading}
          autoFocus
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat;