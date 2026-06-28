import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import PersonalitySelector from './components/PersonalitySelector.jsx';
import SessionSelector from './components/SessionSelector.jsx';
import Chat from './components/Chat.jsx';
import Sidebar from './components/Sidebar';

function AppContent() {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedPersona, setSelectedPersona] = useState(location.state?.persona || null);
  const [selectedSession, setSelectedSession] = useState(location.state?.session || null);

  const handlePersonaSelected = (persona) => {
    setSelectedPersona(persona);
    setSelectedSession(null);
    navigate(`/sessions/${encodeURIComponent(persona.key)}`, { state: { persona } });
  };

  const handleSessionSelected = (session) => {
    const persona = selectedPersona || routePersona || location.state?.persona;
    if (!persona?.key) {
      console.error('No persona selected for session navigation');
      return;
    }

    setSelectedSession(session);
    const targetPath = session
      ? `/chat/${encodeURIComponent(persona.key)}/${session.id}`
      : `/chat/${encodeURIComponent(persona.key)}`;
    navigate(targetPath, { state: { persona, session } });
  };

  const handleBackToPersonalities = () => {
    setSelectedPersona(null);
    setSelectedSession(null);
    navigate('/');
  };

  const handleBackToSessions = () => {
    const persona = selectedPersona || routePersona || location.state?.persona;
    if (!persona?.key) return;
    setSelectedSession(null);
    navigate(`/sessions/${encodeURIComponent(persona.key)}`, { state: { persona } });
  };

  const routePersona = selectedPersona || location.state?.persona;
  const routeSession = selectedSession || location.state?.session;

  return (
    <div className="min-h-screen bg-bg text-text">
      <Routes>
        <Route
          path="/"
          element={<PersonalitySelector onPersonaSelected={handlePersonaSelected} />}
        />
        <Route
          path="/sessions/:personaKey"
          element={
            <SessionSelector
              persona={routePersona}
              onSessionSelected={handleSessionSelected}
              onBack={handleBackToPersonalities}
            />
          }
        />
        <Route
          path="/chat/:personaKey/:sessionId?"
          element={
            <div className="flex h-screen">
            <Sidebar
              activeView="discover"
              onViewChange={() => {}}
              onCreateClick={handleBackToPersonalities}
            />
            <main className="flex-1 overflow-hidden">
              <Chat
                persona={routePersona}
                session={routeSession}
                onBack={handleBackToSessions}
              />
            </main>
          </div>
          }
        />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
