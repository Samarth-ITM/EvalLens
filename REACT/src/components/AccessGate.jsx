import React, { useState } from 'react';
import { Lock, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';

export default function AccessGate({ expectedPasskey, onUnlock }) {
  const [passkeyInput, setPasskeyInput] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (passkeyInput === expectedPasskey) {
      setErrorMsg('');
      onUnlock();
    } else {
      setErrorMsg('Incorrect passkey. Please check your credentials or enter evallens2026.');
    }
  };

  return (
    <div style={{
      minHeight: '80vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem'
    }}>
      <div className="card" style={{ maxWidth: '440px', width: '100%', textAlign: 'center' }}>
        <div style={{
          width: '56px',
          height: '56px',
          background: 'var(--primary-light)',
          color: 'var(--primary)',
          borderRadius: 'var(--radius-full)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1.25rem'
        }}>
          <Lock size={28} />
        </div>

        <h1 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          EvalLens Workspace
        </h1>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: 1.5 }}>
          Private prototype for human and AI evaluation testing. Enter the access passkey to unlock your evaluations.
        </p>

        <form onSubmit={handleSubmit} style={{ textAlign: 'left' }}>
          <div className="form-group">
            <label className="form-label" htmlFor="passkey-input">
              Workspace Passkey
            </label>
            <input
              id="passkey-input"
              type="password"
              className="form-control"
              placeholder="e.g. evallens2026"
              value={passkeyInput}
              onChange={(e) => {
                setPasskeyInput(e.target.value);
                if (errorMsg) setErrorMsg('');
              }}
              autoFocus
              required
            />
          </div>

          {errorMsg && (
            <div className="banner banner-danger" style={{ marginBottom: '1rem', fontSize: '0.85rem' }}>
              <AlertCircle size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }}>
            <span>Access Workspace</span>
            <ArrowRight size={16} />
          </button>
        </form>

        <div style={{
          marginTop: '1.5rem',
          paddingTop: '1rem',
          borderTop: '1px solid var(--border-color)',
          fontSize: '0.75rem',
          color: 'var(--text-muted)'
        }}>
          Default prototype passkey: <code>evallens2026</code>
        </div>
      </div>
    </div>
  );
}
