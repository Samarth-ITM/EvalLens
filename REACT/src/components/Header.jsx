import React from 'react';
import { ShieldCheck, Key, FileText, CheckCircle2, History, Settings, LogOut, Home, PlusCircle } from 'lucide-react';

export default function Header({ activeNav, setActiveNav, onLogout, hasApiKey, evaluationCount }) {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'new', label: 'New Evaluation', icon: PlusCircle },
    { id: 'evaluate', label: 'Evaluate', icon: CheckCircle2 },
    { id: 'history', label: 'History', icon: History, count: evaluationCount },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header style={{
      background: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border-color)',
      padding: '0.875rem 1.5rem',
      borderRadius: 'var(--radius-lg)',
      marginBottom: '1rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '1rem'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }} onClick={() => setActiveNav('home')}>
        <div style={{
          background: 'var(--primary-light)',
          color: 'var(--primary)',
          padding: '0.5rem',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <FileText size={22} />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '1.15rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            EvalLens
            <span style={{ fontSize: '0.65rem', background: 'var(--bg-tertiary)', color: 'var(--text-muted)', padding: '0.15rem 0.4rem', borderRadius: 'var(--radius-sm)' }}>
              v1.0 React
            </span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Human & AI Evaluation Comparison Tool
          </div>
        </div>
      </div>

      <nav style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeNav === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveNav(item.id)}
              className="btn btn-sm"
              style={{
                background: isActive ? 'var(--primary)' : 'transparent',
                color: isActive ? '#ffffff' : 'var(--text-muted)',
                border: isActive ? 'none' : '1px solid transparent',
              }}
            >
              <Icon size={16} />
              <span>{item.label}</span>
              {item.count !== undefined && item.count > 0 && (
                <span style={{
                  background: isActive ? 'rgba(255,255,255,0.25)' : 'var(--bg-tertiary)',
                  color: isActive ? '#ffffff' : 'var(--text-main)',
                  fontSize: '0.7rem',
                  padding: '0.1rem 0.4rem',
                  borderRadius: 'var(--radius-full)',
                  marginLeft: '0.2rem'
                }}>
                  {item.count}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div
          title={hasApiKey ? 'Live Gemini AI key configured' : 'Using smart offline evaluation engine'}
          style={{
            fontSize: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.25rem 0.6rem',
            borderRadius: 'var(--radius-full)',
            background: hasApiKey ? 'var(--success-light)' : 'var(--bg-tertiary)',
            color: hasApiKey ? 'var(--success)' : 'var(--text-muted)'
          }}
        >
          <Key size={13} />
          <span>{hasApiKey ? 'Gemini Live' : 'Offline Engine'}</span>
        </div>

        <button
          onClick={onLogout}
          title="Sign out of workspace"
          className="btn btn-secondary btn-sm"
          style={{ padding: '0.35rem 0.65rem' }}
        >
          <LogOut size={15} />
          <span>Exit</span>
        </button>
      </div>
    </header>
  );
}
