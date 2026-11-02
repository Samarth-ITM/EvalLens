import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  Sparkles,
  Lock,
  ArrowLeft,
  ArrowRight,
  BarChart2,
  AlertCircle,
  Quote,
  Eye,
  EyeOff,
  Home,
  History,
  BookOpen,
  Columns,
  Printer,
  Download,
  CheckCheck,
  FileCheck
} from 'lucide-react';
import { calculateComparison } from '../utils/scoring';
import { evaluateSubmissionAI } from '../utils/gemini';
import DocumentReaderSheet from '../components/DocumentReaderSheet';
import ScoreInput from '../components/ScoreInput';

export default function EvaluatePage({
  evaluations,
  selectedId,
  onSelectEvaluation,
  onUpdateEvaluation,
  onGoHome,
  onGoHistory,
  apiKey,
  model
}) {
  const currentEval = evaluations.find((e) => e.id === selectedId) || evaluations[0];

  const [humanScores, setHumanScores] = useState(currentEval?.human_scores || {});
  const [isSubmittingAI, setIsSubmittingAI] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [showDocumentSheet, setShowDocumentSheet] = useState(true);
  const [splitView, setSplitView] = useState(true);

  // Sync state if selected evaluation changes
  useEffect(() => {
    if (currentEval) {
      setHumanScores(currentEval.human_scores || {});
      setErrorMsg('');
      
      // Always automatically perform AI evaluation if missing
      const hasAI = currentEval.ai_scores && Object.keys(currentEval.ai_scores).length > 0;
      if (!hasAI && !isSubmittingAI) {
        autoRunAI(currentEval);
      }
    }
  }, [currentEval?.id]);

  const autoRunAI = async (evalObj) => {
    setIsSubmittingAI(true);
    try {
      const aiResults = await evaluateSubmissionAI({
        contentText: evalObj.content_text,
        criteria: evalObj.criteria,
        instructions: evalObj.instructions,
        apiKey,
        model
      });
      const updated = {
        ...evalObj,
        ai_scores: aiResults
      };
      onUpdateEvaluation(updated);
    } catch (err) {
      console.warn('AI evaluation warning:', err.message);
    } finally {
      setIsSubmittingAI(false);
    }
  };

  if (!currentEval) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', marginBottom: '1.25rem' }}>
          No evaluations found. Start a new evaluation to begin reviewing documents.
        </p>
        <button className="btn btn-primary" onClick={onGoHome}>
          <Home size={16} />
          <span>Go to Home</span>
        </button>
      </div>
    );
  }

  const isCompleted = currentEval.status === 'completed' || currentEval.status === 'approved';
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

  const handleSubmitHumanScores = () => {
    for (const c of currentEval.criteria) {
      const entry = humanScores[c.id];
      if (!entry || entry.score === undefined || entry.score === null) {
        setErrorMsg(`Please award a score for "${c.name}".`);
        return;
      }
      if (entry.score < 0 || entry.score > c.max_marks) {
        setErrorMsg(`Score for "${c.name}" must be between 0 and ${c.max_marks}.`);
        return;
      }
    }

    setErrorMsg('');
    const updated = {
      ...currentEval,
      human_scores: humanScores,
      status: 'human_submitted'
    };
    onUpdateEvaluation(updated);
  };

  const handleSaveAndApprove = () => {
    const updated = {
      ...currentEval,
      human_scores: humanScores,
      status: 'completed',
      approved_at: new Date().toISOString()
    };
    onUpdateEvaluation(updated);
  };

  const handleExportPDF = () => {
    window.print();
  };

  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(currentEval, null, 2));
    const a = document.createElement('a');
    a.href = dataStr;
    a.download = `${currentEval.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_report.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  const comp = calculateComparison(currentEval.criteria, currentEval.human_scores, currentEval.ai_scores);

  return (
    <div>
      {/* Top Header: Navigation & Action Toolbar (Hidden in Print View) */}
      <div className="no-print" style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-lg)',
        padding: '0.875rem 1.25rem',
        marginBottom: '1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '0.75rem',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: '1 1 300px' }}>
          <label style={{ fontSize: '0.825rem', fontWeight: 700, color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
            Evaluation:
          </label>
          <select
            className="form-control"
            style={{ fontWeight: 600, padding: '0.45rem 0.75rem', fontSize: '0.875rem' }}
            value={currentEval.id}
            onChange={(e) => onSelectEvaluation(e.target.value)}
          >
            {evaluations.map((ev) => (
              <option key={ev.id} value={ev.id}>
                {ev.title} {ev.status === 'completed' ? '(Approved & Completed 🔒)' : '(Active)'}
              </option>
            ))}
          </select>
        </div>

        {/* Action Toolbar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setShowDocumentSheet(!showDocumentSheet)}
            title="Toggle examiner reading paper view"
          >
            <BookOpen size={14} color="var(--primary)" />
            <span>{showDocumentSheet ? 'Hide Paper' : 'View Paper'}</span>
          </button>

          <button
            className={`btn btn-sm ${splitView ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => {
              setSplitView(!splitView);
              if (!showDocumentSheet) setShowDocumentSheet(true);
            }}
            title="Toggle Side-by-Side Split Screen"
          >
            <Columns size={14} />
            <span>{splitView ? 'Side-by-Side (Active)' : 'Stacked View'}</span>
          </button>

          <button
            className="btn btn-secondary btn-sm"
            onClick={handleExportPDF}
            title="Export evaluation as PDF report or print"
          >
            <Printer size={14} />
            <span>Export as PDF</span>
          </button>

          <button
            className="btn btn-secondary btn-sm"
            onClick={handleExportJSON}
            title="Download JSON record"
          >
            <Download size={14} />
            <span>Export JSON</span>
          </button>

          <button className="btn btn-secondary btn-sm" onClick={onGoHistory} title="View all completed evaluations">
            <History size={14} />
            <span>History</span>
          </button>
        </div>
      </div>

      {/* Progress Status Bar (Hidden in Print View) */}
      <div className="no-print" style={{
        background: '#ffffff',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '0.65rem 1.15rem',
        marginBottom: '1.25rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '0.75rem',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', flexWrap: 'wrap' }}>
          <span className={`badge ${hasAIDone ? 'badge-purple' : 'badge-warning'}`}>
            <Sparkles size={11} />
            1. AI Evaluation: {isSubmittingAI ? 'Evaluating...' : (hasAIDone ? 'Ready ✓' : 'Pending')}
          </span>
          <span style={{ color: 'var(--text-tertiary)' }}>➔</span>
          <span className={`badge ${hasHumanDone ? 'badge-success' : 'badge-primary'}`}>
            2. Human Scoring: {hasHumanDone ? 'Scores Submitted ✓' : 'In Progress'}
          </span>
          <span style={{ color: 'var(--text-tertiary)' }}>➔</span>
          <span className={`badge ${isCompleted ? 'badge-success' : 'badge-warning'}`}>
            3. Approval: {isCompleted ? 'Saved & Approved 🔒' : 'Awaiting Approval'}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn btn-secondary btn-sm" onClick={onGoHome}>
            <Home size={14} />
            <span>Dashboard</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="banner banner-danger no-print" style={{ marginBottom: '1.25rem' }}>
          <AlertCircle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Print-Only Academic Report Header */}
      <div className="print-only" style={{ display: 'none', marginBottom: '2rem' }}>
        <div style={{ borderBottom: '2px solid #0f172a', paddingBottom: '1rem', marginBottom: '1rem' }}>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, margin: 0 }}>EvalLens: Academic Assessment Report</h1>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.9rem', color: '#475569' }}>
            <span><strong>Student:</strong> Samarth Navale (Roll: 150096725148)</span>
            <span><strong>Subject:</strong> AI Prompt Engineering &bull; <strong>Professor:</strong> Poonam Ma'am</span>
          </div>
          <div style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.25rem' }}>
            <strong>Document Title:</strong> {currentEval.title} &bull; <strong>Cohort:</strong> Sam Altman
          </div>
        </div>
      </div>

      {/* Main Workspace Layout (Side-by-Side Split View) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: splitView && showDocumentSheet ? 'minmax(400px, 1fr) minmax(460px, 1.25fr)' : '1fr',
        gap: '1.5rem',
        alignItems: 'start'
      }}>
        {/* Left Side: Examiner A4 Paper Reading Sheet */}
        {showDocumentSheet && (
          <div style={{ position: splitView ? 'sticky' : 'static', top: '1.5rem' }}>
            <DocumentReaderSheet
              title={currentEval.title}
              submissionType={currentEval.submission_type}
              contentText={currentEval.content_text}
              wordCount={currentEval.word_count}
            />
          </div>
        )}

        {/* Right Side: Examiner Scoring & Context-Grounded AI Insights */}
        <div>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div className="card-title" style={{ margin: 0 }}>
                <CheckCircle2 size={20} color="var(--primary)" />
                Examiner Evaluation & Scoring
              </div>
              <span className="badge badge-primary">
                {currentEval.criteria.length} Criteria &bull; Total Max {currentEval.criteria.reduce((s, c) => s + c.max_marks, 0)} pts
              </span>
            </div>
            <div className="card-subtitle">
              Inspect the AI suggested marks, reasons, and constructive critique below, then award your score using the interactive 0.5 step controls.
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '1.5rem' }}>
              {currentEval.criteria.map((c) => {
                const h = humanScores[c.id] || currentEval.human_scores?.[c.id] || { score: 0, feedback: '' };
                const aiEntry = currentEval.ai_scores?.[c.id];

                return (
                  <div
                    key={c.id}
                    style={{
                      background: '#ffffff',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      padding: '1.25rem',
                      boxShadow: 'var(--shadow-sm)'
                    }}
                  >
                    {/* Criterion Title & Max Marks */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <div>
                        <span style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-main)' }}>
                          {c.name}
                        </span>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                          {c.description}
                        </div>
                      </div>
                      <span className="badge badge-primary">
                        Max Marks: {c.max_marks} pts
                      </span>
                    </div>

                    {c.scoring_guidance && (
                      <div style={{
                        fontSize: '0.8rem',
                        color: 'var(--text-secondary)',
                        background: 'var(--bg-subtle)',
                        padding: '0.5rem 0.75rem',
                        borderRadius: 'var(--radius-sm)',
                        marginBottom: '0.85rem',
                        borderLeft: '3px solid var(--primary)'
                      }}>
                        <strong>Guidance:</strong> {c.scoring_guidance}
                      </div>
                    )}

                    {/* AI Suggested Mark, Reason & Critic Callout (Always Shown) */}
                    <div style={{
                      background: 'linear-gradient(135deg, #fbfaff 0%, #f5f3ff 100%)',
                      border: '1px solid var(--purple-border)',
                      borderRadius: 'var(--radius-md)',
                      padding: '0.875rem 1rem',
                      marginBottom: '1rem'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span className="badge badge-purple" style={{ fontSize: '0.775rem' }}>
                          <Sparkles size={12} />
                          AI Suggested Mark: {aiEntry?.score !== undefined ? `${aiEntry.score} / ${c.max_marks} pts` : 'Analyzing...'}
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--purple)', fontWeight: 600 }}>
                          Confidence: {aiEntry?.confidence || 'High'}
                        </span>
                      </div>

                      {/* Reason */}
                      <div style={{ fontSize: '0.825rem', color: '#334155', marginBottom: '0.45rem', lineHeight: 1.5 }}>
                        <strong style={{ color: 'var(--purple)' }}>Reason: </strong>
                        {aiEntry?.reason || aiEntry?.rationale || 'Analyzing document context against criterion expectations...'}
                      </div>

                      {/* Critic */}
                      <div style={{ fontSize: '0.825rem', color: '#475569', marginBottom: '0.45rem', lineHeight: 1.5 }}>
                        <strong style={{ color: '#b45309' }}>Critic: </strong>
                        {aiEntry?.critic || 'Evaluating potential omissions, baseline controls, and empirical depth...'}
                      </div>

                      {/* Quoted Evidence */}
                      {aiEntry?.evidence_quote && (
                        <div style={{
                          display: 'flex',
                          gap: '0.4rem',
                          alignItems: 'flex-start',
                          fontSize: '0.775rem',
                          color: '#1e40af',
                          background: '#eff6ff',
                          padding: '0.35rem 0.6rem',
                          borderRadius: 'var(--radius-sm)',
                          borderLeft: '2px solid var(--primary)'
                        }}>
                          <Quote size={12} style={{ flexShrink: 0, marginTop: '2px' }} />
                          <span><strong style={{ color: '#1e40af' }}>Quoted Evidence: </strong><em>"{aiEntry.evidence_quote}"</em></span>
                        </div>
                      )}
                    </div>

                    {/* Interactive Tactile Score Input Component */}
                    <div style={{ marginBottom: '0.75rem' }}>
                      <label className="form-label" style={{ marginBottom: '0.35rem' }}>
                        Your Score (0 - {c.max_marks}):
                      </label>
                      <ScoreInput
                        value={h.score !== undefined ? h.score : 0}
                        maxMarks={c.max_marks}
                        disabled={isCompleted}
                        onChange={(val) => handleScoreChange(c.id, val)}
                      />
                    </div>

                    {/* Qualitative Remarks */}
                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label className="form-label" style={{ fontSize: '0.8rem' }}>
                        Examiner Remarks (Optional)
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Examiner comments or justification..."
                        value={h.feedback || ''}
                        disabled={isCompleted}
                        onChange={(e) => handleFeedbackChange(c.id, e.target.value)}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Primary Action Button: SUBMIT SCORES */}
            {!isCompleted && (
              <div className="no-print" style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
                <button
                  className="btn btn-primary"
                  style={{ padding: '0.75rem 1.75rem', fontSize: '0.95rem', fontWeight: 700 }}
                  onClick={handleSubmitHumanScores}
                >
                  <CheckCircle2 size={18} />
                  <span>SUBMIT SCORES</span>
                </button>
              </div>
            )}
          </div>

          {/* Section 2: Comparison & Final SAVE AND APPROVE */}
          {(hasHumanDone || isCompleted) && (
            <div className="card" style={{ marginTop: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div className="card-title" style={{ margin: 0 }}>
                  <BarChart2 size={20} color="var(--primary)" />
                  Evaluation Comparison & Approval
                </div>
                <span className={`badge ${
                  comp.alignmentCategory === 'Strong Agreement' ? 'badge-success' : 
                  comp.alignmentCategory === 'Moderate Agreement' ? 'badge-warning' : 'badge-danger'
                }`}>
                  {comp.alignmentCategory}
                </span>
              </div>
              <div className="card-subtitle">
                Side-by-side score comparison, variance metrics, and final sign-off.
              </div>

              {/* KPI Stat Boxes */}
              <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
                <div className="stat-box">
                  <div className="stat-value" style={{ color: 'var(--primary)' }}>
                    {comp.humanTotal} <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>/ {comp.maxTotal}</span>
                  </div>
                  <div className="stat-label">Human Score ({comp.humanPct}%)</div>
                </div>

                <div className="stat-box">
                  <div className="stat-value" style={{ color: 'var(--purple)' }}>
                    {comp.aiTotal} <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>/ {comp.maxTotal}</span>
                  </div>
                  <div className="stat-label">AI Suggested ({comp.aiPct}%)</div>
                </div>

                <div className="stat-box">
                  <div className="stat-value" style={{ color: comp.alignmentCategory === 'Strong Agreement' ? 'var(--success)' : 'var(--warning)' }}>
                    {Math.abs(Number((comp.humanTotal - comp.aiTotal).toFixed(1)))} <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>pts</span>
                  </div>
                  <div className="stat-label">Score Difference ({comp.alignmentCategory})</div>
                </div>
              </div>

              {/* Criteria Progress Bars Breakdown */}
              <div style={{ marginBottom: '1.5rem' }}>
                {comp.criterionComparisons.map((c) => {
                  const humanPct = c.maxMarks > 0 ? (c.humanScore / c.maxMarks) * 100 : 0;
                  const aiPct = c.maxMarks > 0 ? (c.aiScore / c.maxMarks) * 100 : 0;

                  return (
                    <div key={c.criterionId} className="comparison-row" style={{ marginBottom: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)' }}>
                          {c.name}
                        </span>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <span className="badge badge-primary">Human: {c.humanScore}/{c.maxMarks}</span>
                          <span className="badge badge-purple">AI: {c.aiScore}/{c.maxMarks}</span>
                          <span className="badge badge-warning">Diff: {c.delta > 0 ? `+${c.delta}` : c.delta} pts</span>
                        </div>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <span style={{ width: '65px', fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>
                            Human
                          </span>
                          <div className="bar-track" style={{ flex: 1 }}>
                            <div className="bar-fill-human" style={{ width: `${humanPct}%` }} />
                          </div>
                          <span style={{ width: '45px', fontSize: '0.75rem', color: 'var(--text-secondary)', textAlign: 'right' }}>
                            {c.humanScore} pts
                          </span>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <span style={{ width: '65px', fontSize: '0.75rem', color: 'var(--purple)', fontWeight: 600 }}>
                            AI
                          </span>
                          <div className="bar-track" style={{ flex: 1 }}>
                            <div className="bar-fill-ai" style={{ width: `${aiPct}%` }} />
                          </div>
                          <span style={{ width: '45px', fontSize: '0.75rem', color: 'var(--text-secondary)', textAlign: 'right' }}>
                            {c.aiScore} pts
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* SAVE AND APPROVE Action Footer */}
              <div className="no-print" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '1rem',
                paddingTop: '1.25rem',
                borderTop: '1px solid var(--border-subtle)',
                marginTop: '1.5rem'
              }}>
                {!isCompleted ? (
                  <button
                    className="btn btn-success"
                    style={{ padding: '0.75rem 1.75rem', fontSize: '0.95rem', fontWeight: 700 }}
                    onClick={handleSaveAndApprove}
                  >
                    <CheckCheck size={18} />
                    <span>SAVE AND APPROVE</span>
                  </button>
                ) : (
                  <div style={{ fontSize: '0.9rem', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 700 }}>
                    <FileCheck size={18} />
                    <span>Evaluation Approved & Locked Successfully</span>
                  </div>
                )}

                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  <button className="btn btn-secondary" onClick={handleExportPDF}>
                    <Printer size={16} />
                    <span>Export as PDF</span>
                  </button>

                  <button className="btn btn-primary" onClick={onGoHome}>
                    <Home size={16} />
                    <span>Return to Dashboard</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
