import React from 'react';
import { Minus, Plus, Award } from 'lucide-react';

export default function ScoreInput({ value, maxMarks = 5, onChange, disabled = false }) {
  const current = typeof value === 'number' && !isNaN(value) ? value : 0;
  const max = Math.max(1, maxMarks);

  // Generate 0.5 increment options up to maxMarks
  const stepOptions = [];
  for (let s = 0; s <= max; s += 0.5) {
    stepOptions.push(Number(s.toFixed(1)));
  }

  const handleStep = (delta) => {
    if (disabled) return;
    const next = Math.min(max, Math.max(0, Number((current + delta).toFixed(1))));
    onChange(next);
  };

  const getQualityBadge = (score, max) => {
    const ratio = max > 0 ? score / max : 0;
    if (ratio >= 0.9) return { label: 'Outstanding (A+)', bg: '#ecfdf5', color: '#059669', border: '#a7f3d0' };
    if (ratio >= 0.75) return { label: 'Proficient (A)', bg: '#eff6ff', color: '#2563eb', border: '#bfdbfe' };
    if (ratio >= 0.5) return { label: 'Acceptable (B)', bg: '#fffbeb', color: '#d97706', border: '#fde68a' };
    return { label: 'Needs Improvement', bg: '#fef2f2', color: '#dc2626', border: '#fecaca' };
  };

  const badge = getQualityBadge(current, max);

  return (
    <div style={{
      background: '#f8fafc',
      border: '1px solid #e2e8f0',
      borderRadius: 'var(--radius-md)',
      padding: '0.85rem 1rem'
    }}>
      {/* Top Row: Score Display + Stepper */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            fontSize: '1.25rem',
            fontWeight: 800,
            color: 'var(--text-main)',
            fontFamily: 'var(--font-mono)',
            background: '#ffffff',
            border: '1px solid #cbd5e1',
            borderRadius: 'var(--radius-sm)',
            padding: '0.2rem 0.6rem',
            minWidth: '70px',
            textAlign: 'center'
          }}>
            {current.toFixed(1)}
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
            / {max} pts
          </span>
          <span style={{
            fontSize: '0.725rem',
            fontWeight: 700,
            padding: '0.2rem 0.55rem',
            borderRadius: 'var(--radius-full)',
            background: badge.bg,
            color: badge.color,
            border: `1px solid ${badge.border}`
          }}>
            {badge.label}
          </span>
        </div>

        {/* Stepper Controls */}
        {!disabled && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleStep(-0.5)}
              disabled={current <= 0}
              title="Decrease by 0.5"
              style={{ width: '32px', height: '32px', padding: 0 }}
            >
              <Minus size={14} />
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleStep(0.5)}
              disabled={current >= max}
              title="Increase by 0.5"
              style={{ width: '32px', height: '32px', padding: 0 }}
            >
              <Plus size={14} />
            </button>
          </div>
        )}
      </div>

      {/* Quick Select Pill Buttons */}
      {!disabled && (
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
            Quick Select (0.5 Step):
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
            {stepOptions.map((opt) => {
              const isSelected = opt === current;
              return (
                <button
                  key={opt}
                  type="button"
                  onClick={() => onChange(opt)}
                  style={{
                    padding: '0.25rem 0.5rem',
                    fontSize: '0.775rem',
                    fontWeight: isSelected ? 700 : 500,
                    borderRadius: 'var(--radius-sm)',
                    border: isSelected ? '1px solid var(--primary)' : '1px solid #cbd5e1',
                    background: isSelected ? 'var(--primary)' : '#ffffff',
                    color: isSelected ? '#ffffff' : 'var(--text-main)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {opt}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
