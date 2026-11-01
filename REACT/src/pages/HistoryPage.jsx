import React, { useState } from 'react';
import { History, Search, Download, Trash2, ArrowRight, CheckCircle2, Clock } from 'lucide-react';
import { calculateComparison } from '../utils/scoring';

export default function HistoryPage({ evaluations, onSelectEvaluation, onDeleteEvaluation }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'completed' | 'in_progress'

  const filtered = evaluations.filter((ev) => {
    const matchesSearch = ev.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (ev.submission_type || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    if (statusFilter === 'completed') return matchesSearch && ev.status === 'completed';
    if (statusFilter === 'in_progress') return matchesSearch && ev.status !== 'completed';
    return matchesSearch;
  });

  const handleExportJSON = (ev) => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(ev, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `${ev.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_eval.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div>
      <div className="card">
        <div className="card-title">
          <History size={20} color="var(--primary)" />
          Evaluation History
        </div>
        <div className="card-subtitle">
          Browse, inspect, and export all past human and AI evaluation records.
        </div>

        {/* Filter Controls */}
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
          <div style={{ flex: '1 1 240px', position: 'relative' }}>
            <input
              type="text"
              className="form-control"
              placeholder="Search by evaluation title or type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div style={{ width: '180px' }}>
            <select
              className="form-control"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="completed">Completed Only 🔒</option>
              <option value="in_progress">In Progress Only</option>
            </select>
          </div>
        </div>

        {/* Evaluation Cards */}
        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            No evaluations match your search filter.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
            {filtered.map((ev) => {
              const comp = calculateComparison(ev.criteria, ev.human_scores, ev.ai_scores);
              const isCompleted = ev.status === 'completed';
              const createdDate = new Date(ev.created_at).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
              });

              return (
                <div
                  key={ev.id}
                  style={{
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    padding: '1.25rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: '1rem'
                  }}
                >
                  <div style={{ flex: '1 1 320px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                      <span className={`badge ${isCompleted ? 'badge-success' : 'badge-warning'}`}>
                        {isCompleted ? 'Completed 🔒' : 'In Progress'}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
                        {ev.submission_type || 'General'}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
                        &bull; {createdDate}
                      </span>
                    </div>

                    <div style={{ fontWeight: 600, fontSize: '1rem', color: 'var(--text-main)', marginBottom: '0.35rem' }}>
                      {ev.title}
                    </div>

                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {ev.criteria?.length || 0} criteria &bull; {ev.word_count || 0} words
                    </div>
                  </div>

                  {/* Score Summary */}
                  {comp.maePct !== null && (
                    <div style={{ textAlign: 'right', minWidth: '140px' }}>
                      <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--primary)' }}>
                        Human: {comp.humanTotal} / {comp.maxTotal} pts
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--purple)', fontWeight: 600 }}>
                        AI: {comp.aiTotal} / {comp.maxTotal} pts
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Diff: {comp.maePct}% MAE
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleExportJSON(ev)}
                      title="Export evaluation as JSON"
                    >
                      <Download size={14} />
                      <span>Export</span>
                    </button>

                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => onSelectEvaluation(ev.id)}
                    >
                      <span>{isCompleted ? 'View' : 'Open'}</span>
                      <ArrowRight size={14} />
                    </button>

                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => {
                        if (confirm(`Delete evaluation "${ev.title}"?`)) {
                          onDeleteEvaluation(ev.id);
                        }
                      }}
                      title="Delete evaluation"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
