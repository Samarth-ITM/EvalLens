import React, { useState } from 'react';
import { Settings, Key, Eye, EyeOff, Check, AlertCircle, RefreshCw, Trash2, ShieldCheck } from 'lucide-react';

export default function SettingsPage({ settings, onSaveSettings, onResetDemoData }) {
  const [apiKey, setApiKey] = useState(settings.geminiApiKey || '');
  const [showKey, setShowKey] = useState(false);
  const [model, setModel] = useState(settings.geminiModel || 'gemini-2.5-flash');
  const [passkey, setPasskey] = useState(settings.passkey || 'evallens2026');
  
  const [isTestingKey, setIsTestingKey] = useState(false);
  const [testStatus, setTestStatus] = useState(null); // { type: 'success' | 'error', message: string }
  const [saveBanner, setSaveBanner] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    onSaveSettings({
      geminiApiKey: apiKey.trim(),
      geminiModel: model,
      passkey: passkey.trim() || 'evallens2026'
    });
    setSaveBanner(true);
    setTimeout(() => setSaveBanner(false), 3000);
  };

  const handleTestKey = async () => {
    if (!apiKey.trim()) {
      setTestStatus({ type: 'error', message: 'Please enter a Gemini API key first.' });
      return;
    }

    setIsTestingKey(true);
    setTestStatus(null);

    try {
      const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey.trim()}`;
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: 'Respond with the word OK.' }] }]
        })
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`API Error (${res.status}): ${errorText}`);
      }

      setTestStatus({ type: 'success', message: 'Gemini API key is valid and connected successfully!' });
    } catch (err) {
      setTestStatus({ type: 'error', message: err.message || 'Failed to connect to Gemini API.' });
    } finally {
      setIsTestingKey(false);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-title">
          <Settings size={20} color="var(--primary)" />
          Application Settings
        </div>
        <div className="card-subtitle">
          Configure your Google Gemini API key, AI model, and prototype access credentials.
        </div>

        {saveBanner && (
          <div className="banner banner-success" style={{ marginBottom: '1.25rem' }}>
            <Check size={16} />
            <span>Settings saved successfully.</span>
          </div>
        )}

        <form onSubmit={handleSave}>
          {/* Gemini AI Config */}
          <div style={{
            background: 'var(--bg-primary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem',
            marginBottom: '1.5rem'
          }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Key size={18} color="var(--primary)" />
              Google Gemini API Configuration
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              Your API key is stored strictly in your browser's local memory and is never shared or transmitted elsewhere. If left blank, EvalLens automatically uses a smart built-in offline engine.
            </p>

            <div className="form-group">
              <label className="form-label" htmlFor="api-key-input">
                Gemini API Key (Optional)
              </label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  id="api-key-input"
                  type={showKey ? 'text' : 'password'}
                  className="form-control"
                  placeholder="AIzaSy..."
                  value={apiKey}
                  onChange={(e) => {
                    setApiKey(e.target.value);
                    setTestStatus(null);
                  }}
                />
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowKey(!showKey)}
                  title={showKey ? 'Hide key' : 'Show key'}
                >
                  {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleTestKey}
                  disabled={isTestingKey || !apiKey.trim()}
                >
                  {isTestingKey ? 'Testing...' : 'Test Key'}
                </button>
              </div>
            </div>

            {testStatus && (
              <div className={`banner ${testStatus.type === 'success' ? 'banner-success' : 'banner-danger'}`} style={{ marginTop: '0.5rem' }}>
                {testStatus.type === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
                <span>{testStatus.message}</span>
              </div>
            )}

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" htmlFor="model-select">
                Default Gemini Model
              </label>
              <select
                id="model-select"
                className="form-control"
                value={model}
                onChange={(e) => setModel(e.target.value)}
              >
                <option value="gemini-2.5-flash">gemini-2.5-flash (Fast, recommended)</option>
                <option value="gemini-3.5-flash-lite">gemini-3.5-flash-lite (Cost-effective)</option>
                <option value="gemini-1.5-flash">gemini-1.5-flash</option>
                <option value="gemini-1.5-pro">gemini-1.5-pro (High capability)</option>
              </select>
            </div>
          </div>

          {/* Access Protection Config */}
          <div style={{
            background: 'var(--bg-primary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem',
            marginBottom: '1.5rem'
          }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ShieldCheck size={18} color="var(--success)" />
              5-Person Workspace Passkey
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              Shared passkey required to access this evaluation prototype.
            </p>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" htmlFor="passkey-setting">
                Passkey
              </label>
              <input
                id="passkey-setting"
                type="text"
                className="form-control"
                value={passkey}
                onChange={(e) => setPasskey(e.target.value)}
                required
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginBottom: '1.5rem' }}>
            <button type="submit" className="btn btn-primary">
              <Check size={16} />
              <span>Save Configuration</span>
            </button>
          </div>
        </form>

        {/* Danger Zone / Demo Data */}
        <div style={{
          paddingTop: '1.5rem',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Demo Benchmark Data</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Restore realistic pre-loaded technical evaluations with human and AI comparison scores.
            </div>
          </div>

          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => {
              if (confirm('Reload demo evaluations? Any custom unsaved records will be reset.')) {
                onResetDemoData();
                alert('Demo evaluations reloaded successfully.');
              }
            }}
          >
            <RefreshCw size={14} />
            <span>Reload Demo Data</span>
          </button>
        </div>
      </div>
    </div>
  );
}

