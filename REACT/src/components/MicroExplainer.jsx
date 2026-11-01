import React, { useState, useEffect } from 'react';
import { Sparkles, FileText, Scale, CheckCircle2, X, ArrowRight, Play } from 'lucide-react';

export default function MicroExplainer() {
  const [isDismissed, setIsDismissed] = useState(() => {
    return localStorage.getItem('evallens_hide_explainer') === 'true';
  });
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    {
      icon: FileText,
      step: 'Step 1',
      title: 'Upload Document',
      desc: 'Drop any essay, report, or code file (up to 5,000 words).',
      color: 'var(--primary)',
      bg: 'var(--primary-light)'
    },
    {
      icon: Scale,
      step: 'Step 2',
      title: 'Review Rubric',
      desc: 'AI builds customized criteria; customize max marks and guidance.',
      color: 'var(--warning)',
      bg: 'var(--warning-light)'
    },
    {
      icon: CheckCircle2,
      step: 'Step 3',
      title: 'Grade & AI Critique',
      desc: 'Score independently, then view AI marks, reasons, and constructive criticism.',
      color: 'var(--purple)',
      bg: 'var(--purple-light)'
    }
  ];

  // Tiny automated step cycle every 3.5s
  useEffect(() => {
    if (isDismissed) return;
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % steps.length);
    }, 3800);
    return () => clearInterval(timer);
  }, [isDismissed, steps.length]);

  const handleDismiss = () => {
    setIsDismissed(true);
    localStorage.setItem('evallens_hide_explainer', 'true');
  };

  const handleRestore = () => {
    setIsDismissed(false);
    localStorage.removeItem('evallens_hide_explainer');
  };

  if (isDismissed) {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '0.75rem' }}>
        <button
          className="btn btn-secondary btn-sm"
          onClick={handleRestore}
          style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}
        >
          <Sparkles size={13} color="var(--primary)" />
          <span>How It Works (Guide)</span>
        </button>
      </div>
    );
  }

  const current = steps[activeStep];
  const StepIcon = current.icon;

  return (
    <div className="explainer-banner">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="badge badge-primary pulse-pill">
            <Sparkles size={12} />
            How EvalLens Works
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Quick 3-step walkthrough
          </span>
        </div>

        <button
          className="btn btn-secondary btn-sm"
          onClick={handleDismiss}
          title="Skip tutorial and dismiss"
          style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
        >
          <span>Skip Guide</span>
          <X size={14} />
        </button>
      </div>

      {/* Step Pills Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', marginBottom: '0.75rem' }}>
        {steps.map((s, idx) => {
          const Icon = s.icon;
          const isActive = idx === activeStep;
          return (
            <div
              key={s.step}
              onClick={() => setActiveStep(idx)}
              style={{
                cursor: 'pointer',
                background: isActive ? '#ffffff' : 'var(--bg-subtle)',
                border: isActive ? `2px solid ${s.color}` : '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '0.65rem 0.75rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem',
                transition: 'all 0.2s ease',
                boxShadow: isActive ? 'var(--shadow-sm)' : 'none'
              }}
            >
              <div style={{
                background: s.bg,
                color: s.color,
                padding: '0.35rem',
                borderRadius: 'var(--radius-sm)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Icon size={16} />
              </div>
              <div style={{ overflow: 'hidden' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)', fontWeight: 600, textTransform: 'uppercase' }}>
                  {s.step}
                </div>
                <div style={{ fontSize: '0.825rem', fontWeight: 700, color: 'var(--text-main)', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                  {s.title}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Dynamic Active Step Explanation */}
      <div style={{
        background: '#ffffff',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '0.75rem 1rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.5rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{ background: current.bg, color: current.color, padding: '0.25rem 0.5rem', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', fontWeight: 700 }}>
            {current.step}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <strong>{current.title}:</strong> {current.desc}
          </div>
        </div>

        <button
          className="btn btn-secondary btn-sm"
          onClick={() => setActiveStep((prev) => (prev + 1) % steps.length)}
          style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
        >
          <span>Next</span>
          <ArrowRight size={13} />
        </button>
      </div>
    </div>
  );
}
