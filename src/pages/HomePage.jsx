import React, { useState } from 'react';
import { Upload, FileText, ArrowRight, CheckCircle2, Clock, Sparkles, AlertCircle } from 'lucide-react';
import { countWords, suggestEvaluationTitle, readFileContent, MAX_FILE_SIZE_BYTES, MAX_SUBMISSION_WORDS } from '../utils/textParser';
import { calculateComparison } from '../utils/scoring';
import MicroExplainer from '../components/MicroExplainer';

export default function HomePage({ evaluations, onStartNewWithContent, onSelectEvaluation, setActiveNav }) {
  const [fastTrackText, setFastTrackText] = useState('');
  const [fileName, setFileName] = useState('');
  const [isReadingFile, setIsReadingFile] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const wordCount = countWords(fastTrackText);
  const isOverWordLimit = wordCount > MAX_SUBMISSION_WORDS;

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadError('');
    setIsReadingFile(true);

    try {
      if (file.size > MAX_FILE_SIZE_BYTES) {
        throw new Error(`File is ${(file.size / (1024 * 1024)).toFixed(1)} MB, exceeding the 10 MB limit.`);
      }

      const content = await readFileContent(file);
      const words = countWords(content);

      if (words > MAX_SUBMISSION_WORDS) {
        setUploadError(`File contains ${words.toLocaleString()} words, exceeding the ${MAX_SUBMISSION_WORDS.toLocaleString()} word limit.`);
        setIsReadingFile(false);
        return;
      }

      setFileName(file.name);
      setFastTrackText(content);
    } catch (err) {
      setUploadError(err.message || 'Could not read file');
    } finally {
      setIsReadingFile(false);
    }
  };

  const handleBegin = () => {
    if (!fastTrackText.trim()) return;
    if (isOverWordLimit) return;

    const suggestedTitle = suggestEvaluationTitle(fileName, fastTrackText);
    onStartNewWithContent({
      title: suggestedTitle,
      contentText: fastTrackText,
      fileName
    });
  };

  // Stats calculation
  const totalCount = evaluations.length;
  const completedList = evaluations.filter((e) => e.status === 'completed');
  const inProgressList = evaluations.filter((e) => e.status !== 'completed');

  return (
    <div>
      {/* Tiny Animated Walkthrough with Skip Option */}
      <MicroExplainer />

      {/* Quick Start Card */}
      <div className="card" style={{ border: '1px solid var(--border-light)' }}>
        <div className="card-title">
          <Sparkles size={20} color="var(--primary)" />
          Start a New Evaluation
        </div>
        <div className="card-subtitle">
          Upload a document or paste text below. We will help you set up an evaluation rubric and compare human scores with AI judgment.
        </div>

        {uploadError && (
          <div className="banner banner-danger" style={{ marginBottom: '1rem' }}>
            <AlertCircle size={16} />
            <span>{uploadError}</span>
          </div>
        )}

        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
            <Upload size={16} />
            <span>{isReadingFile ? 'Reading file...' : 'Upload Document'}</span>
            <input
              type="file"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              accept=".txt,.md,.py,.cpp,.h,.hpp,.java,.js,.ts,.json,.html,.css,.sql,.docx,.pdf"
            />
          </label>
          {fileName && (
            <span style={{ display: 'inline-flex', alignItems: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Selected: <strong>{fileName}</strong>
            </span>
          )}
        </div>

        <div className="form-group" style={{ marginBottom: '0.75rem' }}>
          <textarea
            className="form-control"
            rows={5}
            placeholder="...or paste submission text or code here directly"
            value={fastTrackText}
            onChange={(e) => {
              setFastTrackText(e.target.value);
              if (uploadError) setUploadError('');
            }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ fontSize: '0.8rem', color: isOverWordLimit ? 'var(--danger)' : 'var(--text-muted)' }}>
            <strong>{wordCount.toLocaleString()}</strong> / {MAX_SUBMISSION_WORDS.toLocaleString()} words
            {isOverWordLimit && ' (Limit exceeded. Please shorten the document.)'}
          </div>

          <button
            className="btn btn-primary"
            onClick={handleBegin}
            disabled={!fastTrackText.trim() || isOverWordLimit || isReadingFile}
          >
            <span>Proceed to Evaluation Setup</span>
            <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        <div className="stat-box">
          <div className="stat-value">{totalCount}</div>
          <div className="stat-label">Total Evaluations</div>
        </div>
        <div className="stat-box">
          <div className="stat-value" style={{ color: 'var(--success)' }}>{completedList.length}</div>
          <div className="stat-label">Completed & Locked</div>
        </div>
        <div className="stat-box">
          <div className="stat-value" style={{ color: 'var(--warning)' }}>{inProgressList.length}</div>
          <div className="stat-label">In Progress</div>
        </div>
      </div>

      {/* Recent Evaluations List */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div className="card-title" style={{ margin: 0 }}>
            Recent Evaluations
          </div>
          {evaluations.length > 0 && (
            <button className="btn btn-secondary btn-sm" onClick={() => setActiveNav('history')}>
              View All History
            </button>
          )}
        </div>

        {evaluations.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No evaluations created yet. Upload a document above to get started.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {evaluations.slice(0, 5).map((ev) => {
              const comp = calculateComparison(ev.criteria, ev.human_scores, ev.ai_scores);
              const isDone = ev.status === 'completed';

              return (
                <div
                  key={ev.id}
                  style={{
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    padding: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: '1rem',
                    transition: 'border-color 0.15s'
                  }}
                >
                  <div style={{ flex: '1 1 300px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                      <span className={`badge ${isDone ? 'badge-success' : 'badge-warning'}`}>
                        {isDone ? 'Completed' : 'In Progress'}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
                        {ev.submission_type || 'General'}
                      </span>
                    </div>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-main)', marginBottom: '0.25rem' }}>
                      {ev.title}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {ev.criteria?.length || 0} criteria &bull; {ev.word_count || 0} words
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
                    {isDone && comp.maePct !== null && (
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--primary)' }}>
                          {comp.humanTotal} / {comp.maxTotal} pts ({comp.humanPct}%)
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          Diff: {Math.abs(Number((comp.humanTotal - comp.aiTotal).toFixed(1)))} pts ({comp.alignmentCategory})
                        </div>
                      </div>
                    )}

                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => onSelectEvaluation(ev.id)}
                    >
                      <span>{isDone ? 'View Results' : 'Continue Evaluation'}</span>
                      <ArrowRight size={14} />
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

