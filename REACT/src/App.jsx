import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import AccessGate from './components/AccessGate';
import HomePage from './pages/HomePage';
import NewEvaluationPage from './pages/NewEvaluationPage';
import EvaluatePage from './pages/EvaluatePage';
import HistoryPage from './pages/HistoryPage';
import SettingsPage from './pages/SettingsPage';
import {
  getSettings,
  saveSettings,
  isAuthenticated,
  setAuthenticated,
  getEvaluations,
  saveEvaluation,
  deleteEvaluation,
  resetToDemoData
} from './utils/storage';

export default function App() {
  const [settings, setSettingsState] = useState(() => getSettings());
  const [authed, setAuthedState] = useState(() => isAuthenticated());
  const [evaluations, setEvaluationsState] = useState(() => getEvaluations());
  const [activeNav, setActiveNav] = useState('home');
  const [selectedEvalId, setSelectedEvalId] = useState(null);
  const [pendingNewSubmission, setPendingNewSubmission] = useState(null);

  // Sync state if evaluations change
  const refreshEvaluations = () => {
    setEvaluationsState(getEvaluations());
  };

  const handleUnlock = () => {
    setAuthenticated(true);
    setAuthedState(true);
  };

  const handleLogout = () => {
    setAuthenticated(false);
    setAuthedState(false);
  };

  const handleStartNewWithContent = ({ title, contentText, fileName }) => {
    setPendingNewSubmission({ title, contentText, fileName });
    setActiveNav('new');
  };

  const handleEvaluationCreated = (newEval) => {
    saveEvaluation(newEval);
    refreshEvaluations();
    setSelectedEvalId(newEval.id);
    setPendingNewSubmission(null);
    setActiveNav('evaluate');
  };

  const handleUpdateEvaluation = (updated) => {
    saveEvaluation(updated);
    refreshEvaluations();
  };

  const handleDeleteEvaluation = (id) => {
    deleteEvaluation(id);
    refreshEvaluations();
    if (selectedEvalId === id) {
      setSelectedEvalId(null);
    }
  };

  const handleSaveSettings = (newSettings) => {
    saveSettings(newSettings);
    setSettingsState(newSettings);
  };

  const handleResetDemoData = () => {
    const fresh = resetToDemoData();
    setEvaluationsState(fresh);
    setSelectedEvalId(fresh[0]?.id || null);
  };

  // If not authenticated, show Access Passkey Gate
  if (!authed) {
    return (
      <AccessGate
        expectedPasskey={settings.passkey || 'evallens2026'}
        onUnlock={handleUnlock}
      />
    );
  }

  const activeId = selectedEvalId || evaluations[0]?.id || null;

  return (
    <div className="app-container">
      <Header
        activeNav={activeNav}
        setActiveNav={setActiveNav}
        onLogout={handleLogout}
        hasApiKey={Boolean(settings.geminiApiKey?.trim())}
        evaluationCount={evaluations.length}
      />

      <main className="main-content">
        {activeNav === 'home' && (
          <HomePage
            evaluations={evaluations}
            onStartNewWithContent={handleStartNewWithContent}
            onSelectEvaluation={(id) => {
              setSelectedEvalId(id);
              setActiveNav('evaluate');
            }}
            setActiveNav={setActiveNav}
          />
        )}

        {activeNav === 'new' && (
          <NewEvaluationPage
            initialData={pendingNewSubmission}
            onEvaluationCreated={handleEvaluationCreated}
            apiKey={settings.geminiApiKey}
            model={settings.geminiModel}
          />
        )}

        {activeNav === 'evaluate' && (
          <EvaluatePage
            evaluations={evaluations}
            selectedId={activeId}
            onSelectEvaluation={(id) => setSelectedEvalId(id)}
            onUpdateEvaluation={handleUpdateEvaluation}
            onGoHome={() => setActiveNav('home')}
            onGoHistory={() => setActiveNav('history')}
            apiKey={settings.geminiApiKey}
            model={settings.geminiModel}
          />
        )}

        {activeNav === 'history' && (
          <HistoryPage
            evaluations={evaluations}
            onSelectEvaluation={(id) => {
              setSelectedEvalId(id);
              setActiveNav('evaluate');
            }}
            onDeleteEvaluation={handleDeleteEvaluation}
          />
        )}

        {activeNav === 'settings' && (
          <SettingsPage
            settings={settings}
            onSaveSettings={handleSaveSettings}
            onResetDemoData={handleResetDemoData}
          />
        )}
      </main>

      <footer style={{
        marginTop: '3rem',
        paddingTop: '1.25rem',
        borderTop: '1px solid var(--border-color)',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-subtle)'
      }}>
        EvalLens &bull; Human Judgment + AI Rubric Comparison &bull; Standalone React Prototype
      </footer>
    </div>
  );
}

