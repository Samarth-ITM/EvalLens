import React, { useState } from 'react';
import { CheckCircle2, Sparkles, Lock, ArrowLeft, ArrowRight, BarChart2, AlertCircle, Quote, Eye } from 'lucide-react';
import { calculateComparison } from '../utils/scoring';
import { evaluateSubmissionAI } from '../utils/gemini';

export default function EvaluatePage({
  evaluations,
  selectedId,
  onSelectEvaluation,
  onUpdateEvaluation,
  apiKey,
  model
}) {
  const currentEval = evaluations.find((e) => e.id === selectedId) || evaluations[0];

  const [humanScores, setHumanScores] = useState(currentEval?.human_scores || {});
  const [isSubmittingAI, setIsSubmittingAI] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [showDocumentDrawer, setShowDocumentDrawer] = useState(false);

  if (!currentEval) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>No evaluations available yet. Create one to begin scoring.</p>
      </div>
    );
  }

  const isCompleted = currentEval.status === 'completed';
  const hasHumanDone = Object.keys(currentEval.human_scores || {}).length > 0;
  const hasAIDone = Object.keys(currentEval.ai_scores || {}).length > 0;

  const handleScoreChange = (critId, value) => {
    const num = parseFloat(value);
    setHumanScores({
      ...humanScores,
      [critId]: {
        ...(humanScores[critId] || {}),
        score: isNaN(num) ? 0 : num
      }
    });
  };

  const handleFeedbackChange = (critId, text) => {
    setHumanScores({
      ...humanScores,
      [critId]: {
        ...(humanScores[critId] || {}),
        feedback: text
      }
    });
  };

  const handleSubmitHuman = () => {
    // Validate that every criterion is scored and within bounds
    for (const c of currentEval.criteria) {
      const entry = humanScores[c.id];
      if (!entry || entry.score === undefined || entry.score === null) {
        setErrorMsg(`Please enter a score for "${c.name}".`);
        return;
      }
      if (entry.score < 0 || entry.score > c.max_marks) {
        setErrorMsg(`Score for "${c.name}" must be between 0 and ${c.max_marks}.`);
        return;
      }
      // Check 0.5 increments
      const remainder = (entry.score * 10) % 5;
      if (remainder !== 0) {
        setErrorMsg(`Score for "${c.name}" must use 0.5 increments (e.g. 0, 0.5, 1.0, 1.5).`);
        return;
      }
    }

    setErrorMsg('');
    const updated = {
      ...currentEval,
      human_scores: humanScores,
      status: hasAIDone ? 'completed' : 'human_completed'
    };
    onUpdateEvaluation(updated);
  };

  const handleRunAI = async () => {
    setIsSubmittingAI(true);
    setErrorMsg('');

    try {
      const aiResults = await evaluateSubmissionAI({
        contentText: currentEval.content_text,
        criteria: currentEval.criteria,
        instructions: currentEval.instructions,
        apiKey,
        model
      });

      const updated = {
        ...currentEval,
        ai_scores: aiResults,
        status: hasHumanDone ? 'completed' : currentEval.status
      };
      onUpdateEvaluation(updated);
    } catch (err) {
      setErrorMsg(err.message || 'Error running AI evaluation');
    } finally {
      setIsSubmittingAI(false);
    }
  };

  const handleLockEvaluation = () => {
    const updated = {
      ...currentEval,
      status: 'completed'
    };
    onUpdateEvaluation(updated);
  };

  const comp = calculateComparison(currentEval.criteria, currentEval.human_scores, currentEval.ai_scores);

  return (
    <div>
      {/* Session Header & Switcher */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <select
            className="form-control"
            style={{ width: 'auto', minWidth: '280px', fontWeight: 600 }}
            value={currentEval.id}
            onChange={(e) => onSelectEvaluation(e.target.value)}
          >
            {evaluations.map((ev) => (
              <option key={ev.id} value={ev.id}>
                {ev.title} ({ev.status === 'completed' ? 'Completed 🔒' : 'In Progress'})
              </option>
            ))}
          </select>
        </div>

        <button
          className="btn btn-secondary btn-sm"
          onClick={() => setShowDocumentDrawer(!showDocumentDrawer)}
        >
          <Eye size={15} />
          <span>{showDocumentDrawer ? 'Hide Document Preview' : 'View Submitted Document'}</span>
        </button>
      </div>

      {/* Lock Banner if Completed */}
      {isCompleted && (
        <div className="banner banner-info">
          <Lock size={18} />
          <span>
            <strong>Locked Evaluation:</strong> This evaluation is completed. You are viewing read-only historical results.
          </span>
        </div>
      )}

      {/* Workflow Progress Breadcrumbs */}
      <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
        <strong>Progress: </strong>
        <span style={{ color: hasHumanDone ? 'var(--success)' : 'var(--primary)' }}>
          1. Human Scoring {hasHumanDone ? '✅' : '(Active)'}
        </span>
        {' ➔ '}
        <span style={{ color: hasAIDone ? 'var(--purple)' : (hasHumanDone ? 'var(--primary)' : 'var(--text-subtle)') }}>
          2. AI Evaluation {hasAIDone ? '✅' : (hasHumanDone ? '(Ready)' : '')}
        </span>
        {' ➔ '}
        <span style={{ color: isCompleted ? 'var(--success)' : 'var(--text-subtle)' }}>
          3. Comparison Dashboard {isCompleted ? '🔒' : ''}
        </span>
      </div>

      {/* Expandable Document Preview */}
      {showDocumentDrawer && (
        <div className="card" style={{ marginBottom: '1.5rem', background: '#090d16' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              Submitted Document Text ({currentEval.word_count || 0} words)
            </span>
          </div>
          <div className="code-preview">
            {currentEval.content_text}
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="banner banner-danger" style={{ marginBottom: '1rem' }}>
          <AlertCircle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* 1. Human Scoring Form */}
      <div className="card">
        <div className="card-title">
          <CheckCircle2 size={20} color="var(--primary)" />
          Human Scoring
        </div>
        <div className="card-subtitle">
          {isCompleted
            ? 'Human scores and feedback recorded for this session.'
            : 'Enter your scores between 0 and the maximum marks using 0.5 increments.'}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
          {currentEval.criteria.map((c) => {
            const h = humanScores[c.id] || currentEval.human_scores?.[c.id] || { score: 0, feedback: '' };

            return (
              <div
                key={c.id}
                style={{
                  background: 'var(--bg-primary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <div>
                    <span style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-main)' }}>
                      {c.name}
                    </span>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      {c.description}
                    </div>
                  </div>
                  <div className="badge badge-primary">
                    Max: {c.max_marks} pts
                  </div>
                </div>

                {c.scoring_guidance && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontStyle: 'italic', marginBottom: '0.75rem' }}>
                    Guidance: {c.scoring_guidance}
                  </div>
                )}

                <div className="grid-2">
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">
                      Your Score (0 - {c.max_marks})
                    </label>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      max={c.max_marks}
                      className="form-control"
                      value={h.score !== undefined ? h.score : 0}
                      disabled={isCompleted}
                      onChange={(e) => handleScoreChange(c.id, e.target.value)}
                    />
                  </div>

                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">
                      Qualitative Remarks (Optional)
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Feedback justification..."
                      value={h.feedback || ''}
                      disabled={isCompleted}
                      onChange={(e) => handleFeedbackChange(c.id, e.target.value)}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {!isCompleted && (
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button className="btn btn-primary" onClick={handleSubmitHuman}>
              <CheckCircle2 size={16} />
              <span>Submit Human Scores</span>
            </button>
          </div>
        )}
      </div>

      {/* 2. AI Evaluation Trigger */}
      {hasHumanDone && !hasAIDone && !isCompleted && (
        <div className="card" style={{ border: '1px solid var(--purple)' }}>
          <div className="card-title">
            <Sparkles size={20} color="var(--purple)" />
            Run Optional AI Rubric Scoring
          </div>
          <div className="card-subtitle">
            Trigger independent AI scoring with Google Gemini to evaluate the submission against the approved rubric.
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              className="btn"
              style={{ background: 'var(--purple)', color: 'white' }}
              onClick={handleRunAI}
              disabled={isSubmittingAI}
            >
              <Sparkles size={16} />
              <span>{isSubmittingAI ? 'Evaluating with Gemini...' : 'Run AI Evaluation with Gemini'}</span>
            </button>
          </div>
        </div>
      )}

      {/* 3. Comparison Dashboard */}
      {hasHumanDone && hasAIDone && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div className="card-title" style={{ margin: 0 }}>
              <BarChart2 size={20} color="var(--primary)" />
              Comparison Dashboard: Human vs. AI
            </div>
            <span className={`badge ${
              comp.alignmentCategory === 'Strong Agreement' ? 'badge-success' : 
              comp.alignmentCategory === 'Moderate Agreement' ? 'badge-warning' : 'badge-danger'
            }`}>
              {comp.alignmentCategory}
            </span>
          </div>
          <div className="card-subtitle">
            Side-by-side alignment metrics, score variance, and evidence citations.
          </div>

          {/* Metric KPI Cards */}
          <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
            <div className="stat-box">
              <div className="stat-value" style={{ color: 'var(--primary)' }}>
                {comp.humanTotal} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ {comp.maxTotal}</span>
              </div>
              <div className="stat-label">Human Score ({comp.humanPct}%)</div>
            </div>

            <div className="stat-box">
              <div className="stat-value" style={{ color: 'var(--purple)' }}>
                {comp.aiTotal} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ {comp.maxTotal}</span>
              </div>
              <div className="stat-label">AI Suggestion ({comp.aiPct}%)</div>
            </div>

            <div className="stat-box">
              <div className="stat-value">
                {comp.maePct !== null ? `${comp.maePct}%` : 'N/A'}
              </div>
              <div className="stat-label">Mean Abs Error (MAE)</div>
            </div>

            <div className="stat-box">
              <div className="stat-value">
                {comp.directionalBias > 0 ? `+${comp.directionalBias}` : comp.directionalBias}
              </div>
              <div className="stat-label">Directional Bias (pts)</div>
            </div>
          </div>

          {/* Dual Bar Charts Per Criterion */}
          <div style={{ marginBottom: '1.5rem' }}>
            <h4 style={{ fontSize: '0.9rem', marginBottom: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Score Breakdown Per Criterion
            </h4>

            {comp.criterionComparisons.map((c) => {
              const humanPct = c.maxMarks > 0 ? (c.humanScore / c.maxMarks) * 100 : 0;
              const aiPct = c.maxMarks > 0 ? (c.aiScore / c.maxMarks) * 100 : 0;

              return (
                <div key={c.criterionId} className="comparison-row">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{c.name}</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Diff: {c.delta > 0 ? `+${c.delta}` : c.delta} pts ({c.normalizedErrorPct}%)
                    </span>
                  </div>

                  {/* Human Bar */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{ width: '60px', fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>
                      Human: {c.humanScore}
                    </span>
                    <div className="bar-track" style={{ flex: 1 }}>
                      <div className="bar-fill-human" style={{ width: `${humanPct}%` }} />
                    </div>
                  </div>

                  {/* AI Bar */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{ width: '60px', fontSize: '0.75rem', color: 'var(--purple)', fontWeight: 600 }}>
                      AI: {c.aiScore}
                    </span>
                    <div className="bar-track" style={{ flex: 1 }}>
                      <div className="bar-fill-ai" style={{ width: `${aiPct}%` }} />
                    </div>
                  </div>

                  {/* Evidence & Rationale Drawer */}
                  <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
                    {c.aiRationale && (
                      <div style={{ color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                        <strong>AI Rationale:</strong> {c.aiRationale}
                      </div>
                    )}
                    {c.evidenceQuote && (
                      <div style={{
                        display: 'flex',
                        gap: '0.4rem',
                        alignItems: 'flex-start',
                        color: '#93c5fd',
                        background: 'rgba(59, 130, 246, 0.1)',
                        padding: '0.4rem 0.6rem',
                        borderRadius: 'var(--radius-sm)'
                      }}>
                        <Quote size={13} style={{ flexShrink: 0, marginTop: '2px' }} />
                        <span><em>"{c.evidenceQuote}"</em></span>
                      </div>
                    )}
                    {c.humanFeedback && (
                      <div style={{ color: 'var(--text-subtle)', marginTop: '0.35rem' }}>
                        <strong>Human Remarks:</strong> {c.humanFeedback}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {!isCompleted && (
            <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <button className="btn btn-success" onClick={handleLockEvaluation}>
                <Lock size={16} />
                <span>Mark Evaluation as Completed & Lock</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
