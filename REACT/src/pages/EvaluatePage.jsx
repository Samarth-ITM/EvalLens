import React, { useState } from 'react';
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
  MessageSquare,
  AlertTriangle,
  Lightbulb
} from 'lucide-react';
import { calculateComparison } from '../utils/scoring';
import { evaluateSubmissionAI } from '../utils/gemini';
import DocumentReaderSheet from '../components/DocumentReaderSheet';

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
  const [splitView, setSplitView] = useState(false);

  // Sync state if selected evaluation changes
  React.useEffect(() => {
    if (currentEval) {
      setHumanScores(currentEval.human_scores || {});
      setErrorMsg('');
    }
  }, [currentEval?.id]);

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

  const handleSaveAndDone = () => {
    if (currentEval.status !== 'completed' && (hasHumanDone || hasAIDone)) {
      const updated = {
        ...currentEval,
        status: 'completed'
      };
      onUpdateEvaluation(updated);
    }
    if (onGoHome) {
      onGoHome();
    }
  };

  const comp = calculateComparison(currentEval.criteria, currentEval.human_scores, currentEval.ai_scores);

  return (
    <div>
      {/* Top Header: Session Selection & Examiner View Controls */}
      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-lg)',
        padding: '1rem 1.25rem',
        marginBottom: '1.25rem',
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
                {ev.title} {ev.status === 'completed' ? '(Completed 🔒)' : '(In Progress)'}
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
            <span>{showDocumentSheet ? 'Hide Document Paper' : 'View Document Paper'}</span>
          </button>

          <button
            className={`btn btn-sm ${splitView ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => {
              setSplitView(!splitView);
              if (!showDocumentSheet) setShowDocumentSheet(true);
            }}
            title="Split screen: read paper on left, score on right"
          >
            <Columns size={14} />
            <span>{splitView ? 'Stacked View' : 'Side-by-Side'}</span>
          </button>

          <button className="btn btn-secondary btn-sm" onClick={onGoHistory} title="View all completed evaluations">
            <History size={14} />
            <span>History</span>
          </button>
        </div>
      </div>

      {/* Persistent Navigation & Save Bar */}
      <div style={{
        background: '#ffffff',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '0.75rem 1.25rem',
        marginBottom: '1.25rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '0.75rem',
        boxShadow: 'var(--shadow-sm)'
      }}>
        {/* Progress pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem', flexWrap: 'wrap' }}>
          <span className={`badge ${hasHumanDone ? 'badge-success' : 'badge-primary'}`}>
            1. Human Scoring: {hasHumanDone ? 'Submitted ✓' : 'In Progress'}
          </span>
          <span style={{ color: 'var(--text-tertiary)' }}>➔</span>
          <span className={`badge ${hasAIDone ? 'badge-purple' : 'badge-warning'}`}>
            2. AI Evaluation: {hasAIDone ? 'Ready ✓' : 'Optional / Next'}
          </span>
          <span style={{ color: 'var(--text-tertiary)' }}>➔</span>
          <span className={`badge ${isCompleted ? 'badge-success' : 'badge-primary'}`}>
            3. Comparison: {isCompleted ? 'Saved & Locked 🔒' : 'Draft'}
          </span>
        </div>

        {/* Direct Action Buttons: Proceed to Dashboard & Previous Results */}
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button
            className="btn btn-primary btn-sm"
            onClick={handleSaveAndDone}
            title="Save your current scores and proceed to dashboard"
          >
            <Home size={14} />
            <span>Save & Done (Dashboard)</span>
          </button>

          <button
            className="btn btn-secondary btn-sm"
            onClick={onGoHistory}
            title="View previous evaluation results"
          >
            <History size={14} />
            <span>Previous Results</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="banner banner-danger" style={{ marginBottom: '1.25rem' }}>
          <AlertCircle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Workspace Layout (Supports Split Mode) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: splitView && showDocumentSheet ? 'minmax(420px, 1fr) minmax(460px, 1.2fr)' : '1fr',
        gap: '1.5rem',
        alignItems: 'start'
      }}>
        {/* Left Side: Examiner Document Reading Sheet */}
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

        {/* Right Side (or Below): Scoring & Comparison */}
        <div>
          {/* Section 1: Human Scoring Card */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div className="card-title" style={{ margin: 0 }}>
                <CheckCircle2 size={20} color="var(--primary)" />
                Examiner Human Scoring
              </div>
              <span className="badge badge-primary">
                {currentEval.criteria.length} Criteria &bull; Total Max {currentEval.criteria.reduce((s, c) => s + c.max_marks, 0)} pts
              </span>
            </div>
            <div className="card-subtitle">
              Read the document and enter your score for each criterion (0.5 mark increments). You can also run AI evaluation below to inspect AI suggested marks, reasons, and critique.
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

                    {/* AI Suggested Mark, Reason & Critic Callout (When AI Scores are Available) */}
                    {aiEntry && (
                      <div style={{
                        background: 'linear-gradient(135deg, #fbfaff 0%, #f5f3ff 100%)',
                        border: '1px solid var(--purple-border)',
                        borderRadius: 'var(--radius-md)',
                        padding: '0.875rem 1rem',
                        marginBottom: '1rem'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                          <span className="badge badge-purple">
                            <Sparkles size={12} />
                            AI Suggested Mark: {aiEntry.score} / {c.max_marks} pts
                          </span>
                          <span style={{ fontSize: '0.75rem', color: 'var(--purple)', fontWeight: 600 }}>
                            Confidence: {aiEntry.confidence || 'High'}
                          </span>
                        </div>

                        {/* Reason */}
                        <div style={{ fontSize: '0.825rem', color: '#334155', marginBottom: '0.4rem', lineHeight: 1.5 }}>
                          <strong style={{ color: 'var(--purple)' }}>Reason: </strong>
                          {aiEntry.reason || aiEntry.rationale || 'Meets standard expectations for this criterion based on the submitted text.'}
                        </div>

                        {/* Critic */}
                        <div style={{ fontSize: '0.825rem', color: '#475569', marginBottom: '0.4rem', lineHeight: 1.5 }}>
                          <strong style={{ color: '#b45309' }}>Critic: </strong>
                          {aiEntry.critic || 'Could provide deeper empirical evidence and expand on edge-case considerations.'}
                        </div>

                        {/* Quoted Evidence */}
                        {aiEntry.evidence_quote && (
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
                            <span><em>"{aiEntry.evidence_quote}"</em></span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Human Score Input & Remarks */}
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
                          Examiner Remarks (Optional)
                        </label>
                        <input
                          type="text"
                          className="form-control"
                          placeholder="Your comments or justification..."
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

            {/* Human Score Submission & AI Run Buttons */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
              <button
                className="btn btn-secondary"
                style={{ color: 'var(--purple)', borderColor: 'var(--purple-border)' }}
                onClick={handleRunAI}
                disabled={isSubmittingAI}
              >
                <Sparkles size={16} />
                <span>{isSubmittingAI ? 'Evaluating with Gemini...' : (hasAIDone ? 'Re-run AI Evaluation' : 'Run AI Evaluation')}</span>
              </button>

              {!isCompleted && (
                <button className="btn btn-primary" onClick={handleSubmitHuman}>
                  <CheckCircle2 size={16} />
                  <span>Submit Human Scores</span>
                </button>
              )}
            </div>
          </div>

          {/* Section 2: Comparison Dashboard (Rendered when both human & AI are done, or when evaluation is completed) */}
          {(hasAIDone || isCompleted) && (
            <div className="card" style={{ marginTop: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div className="card-title" style={{ margin: 0 }}>
                  <BarChart2 size={20} color="var(--primary)" />
                  Evaluation Comparison: Human vs. AI
                </div>
                <span className={`badge ${
                  comp.alignmentCategory === 'Strong Agreement' ? 'badge-success' : 
                  comp.alignmentCategory === 'Moderate Agreement' ? 'badge-warning' : 'badge-danger'
                }`}>
                  {comp.alignmentCategory}
                </span>
              </div>
              <div className="card-subtitle">
                Side-by-side score comparison, detailed AI suggested mark, reason, and constructive critique per criterion.
              </div>

              {/* Simplified KPI Boxes (Zero Fluff) */}
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

              {/* Detailed Breakdown Per Criterion */}
              <div style={{ marginBottom: '1.5rem' }}>
                <h4 style={{ fontSize: '0.85rem', marginBottom: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Detailed Criteria Breakdown & Critique
                </h4>

                {comp.criterionComparisons.map((c) => {
                  const humanPct = c.maxMarks > 0 ? (c.humanScore / c.maxMarks) * 100 : 0;
                  const aiPct = c.maxMarks > 0 ? (c.aiScore / c.maxMarks) * 100 : 0;

                  return (
                    <div key={c.criterionId} className="comparison-row" style={{ marginBottom: '1rem' }}>
                      {/* Criterion Header */}
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

                      {/* Visual Comparison Progress Bars */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginBottom: '0.85rem' }}>
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

                      {/* AI Suggested Mark, Reason, Critic & Evidence Callout */}
                      <div style={{
                        background: '#f8fafc',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        padding: '0.85rem 1rem',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem'
                      }}>
                        {/* 1. AI Suggested Mark */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}>
                          <Sparkles size={14} color="var(--purple)" />
                          <strong style={{ color: 'var(--purple)' }}>AI Suggested Mark:</strong>
                          <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                            {c.aiScore} / {c.maxMarks} pts
                          </span>
                        </div>

                        {/* 2. Reason */}
                        <div style={{ fontSize: '0.825rem', color: '#334155', lineHeight: 1.5 }}>
                          <strong style={{ color: '#0369a1' }}>Reason: </strong>
                          {c.aiReason || c.aiRationale || 'The submission directly demonstrates the necessary requirements for this criterion.'}
                        </div>

                        {/* 3. Critic */}
                        <div style={{ fontSize: '0.825rem', color: '#334155', lineHeight: 1.5 }}>
                          <strong style={{ color: '#b45309' }}>Critic: </strong>
                          {c.aiCritic || 'The presentation could be strengthened by incorporating comparative benchmarks and addressing edge-case limitations.'}
                        </div>

                        {/* 4. Quoted Evidence */}
                        {c.evidenceQuote && (
                          <div style={{
                            display: 'flex',
                            gap: '0.4rem',
                            alignItems: 'flex-start',
                            fontSize: '0.775rem',
                            color: '#1e40af',
                            background: '#eff6ff',
                            padding: '0.4rem 0.65rem',
                            borderRadius: 'var(--radius-sm)',
                            borderLeft: '2px solid var(--primary)',
                            marginTop: '0.2rem'
                          }}>
                            <Quote size={12} style={{ flexShrink: 0, marginTop: '2px' }} />
                            <span><em>"{c.evidenceQuote}"</em></span>
                          </div>
                        )}

                        {/* Human Feedback */}
                        {c.humanFeedback && (
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.4rem', marginTop: '0.2rem' }}>
                            <strong>Examiner Remarks:</strong> {c.humanFeedback}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Bottom Action Footer with Clear Buttons */}
              <div style={{
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
                  <button className="btn btn-success" onClick={handleLockEvaluation}>
                    <Lock size={16} />
                    <span>Mark Evaluation as Completed & Lock</span>
                  </button>
                ) : (
                  <div style={{ fontSize: '0.85rem', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600 }}>
                    <CheckCircle2 size={16} />
                    <span>Evaluation completed and locked in history.</span>
                  </div>
                )}

                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  <button className="btn btn-primary" onClick={handleSaveAndDone}>
                    <Home size={16} />
                    <span>Save & Done (Proceed to Dashboard)</span>
                  </button>
                  <button className="btn btn-secondary" onClick={onGoHistory}>
                    <History size={16} />
                    <span>View Previous Results</span>
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
