import React, { useState } from 'react';
import { FileText, Copy, Check, ZoomIn, ZoomOut, Hash, BookOpen } from 'lucide-react';

export default function DocumentReaderSheet({ title, submissionType, contentText, wordCount }) {
  const [fontSize, setFontSize] = useState(15);
  const [showLineNumbers, setShowLineNumbers] = useState(true);
  const [copied, setCopied] = useState(false);

  const lines = (contentText || '').split('\n');
  const readTimeMin = Math.max(1, Math.ceil((wordCount || 1) / 220));

  const handleCopy = () => {
    navigator.clipboard.writeText(contentText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="paper-sheet">
      {/* Paper Header */}
      <div className="paper-sheet-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span className="badge badge-primary">
              <BookOpen size={12} />
              Examiner Reading Sheet
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
              {submissionType || 'Document'} &bull; ~{readTimeMin} min read
            </span>
          </div>
          <h2 className="paper-sheet-title">{title || 'Untitled Document'}</h2>
        </div>

        {/* Reader Controls Toolbar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setShowLineNumbers(!showLineNumbers)}
            title="Toggle line numbers"
            style={{ padding: '0.25rem 0.5rem' }}
          >
            <Hash size={13} color={showLineNumbers ? 'var(--primary)' : 'var(--text-tertiary)'} />
          </button>

          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setFontSize((s) => Math.max(12, s - 1))}
            title="Decrease font size"
            style={{ padding: '0.25rem 0.5rem' }}
          >
            <ZoomOut size={13} />
          </button>

          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setFontSize((s) => Math.min(20, s + 1))}
            title="Increase font size"
            style={{ padding: '0.25rem 0.5rem' }}
          >
            <ZoomIn size={13} />
          </button>

          <button
            className="btn btn-secondary btn-sm"
            onClick={handleCopy}
            title="Copy text"
            style={{ padding: '0.25rem 0.5rem' }}
          >
            {copied ? <Check size={13} color="var(--success)" /> : <Copy size={13} />}
          </button>
        </div>
      </div>

      {/* Paper Document Body */}
      <div className="paper-sheet-content" style={{ fontSize: `${fontSize}px` }}>
        {lines.map((line, idx) => {
          const isHeading = line.trim().startsWith('#');
          const isCodeBlock = line.trim().startsWith('```') || line.trim().startsWith('CREATE') || line.trim().startsWith('ALTER') || line.trim().startsWith('import ') || line.trim().startsWith('def ');

          return (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'baseline',
                gap: '1rem',
                minHeight: '1.5em',
                lineHeight: isHeading ? '1.4' : '1.75',
                marginTop: isHeading ? '0.75rem' : '0'
              }}
            >
              {showLineNumbers && (
                <span style={{
                  width: '32px',
                  flexShrink: 0,
                  fontSize: '0.725rem',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--text-tertiary)',
                  userSelect: 'none',
                  textAlign: 'right'
                }}>
                  {idx + 1}
                </span>
              )}

              <span style={{
                flex: 1,
                fontWeight: isHeading ? 700 : 400,
                color: isHeading ? 'var(--text-main)' : (isCodeBlock ? '#1e40af' : '#1e293b'),
                fontFamily: isCodeBlock ? 'var(--font-mono)' : 'inherit',
                fontSize: isHeading ? '1.1em' : 'inherit'
              }}>
                {line || '\u00A0'}
              </span>
            </div>
          );
        })}
      </div>

      {/* Paper Footer with Word Count */}
      <div style={{
        marginTop: '1.25rem',
        paddingTop: '0.75rem',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '0.75rem',
        color: 'var(--text-tertiary)'
      }}>
        <span>Total Extracted Words: <strong>{(wordCount || 0).toLocaleString()}</strong></span>
        <span>Examiner Grounding View</span>
      </div>
    </div>
  );
}
