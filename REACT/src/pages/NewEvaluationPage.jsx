import React, { useState } from 'react';
import { Sparkles, Edit3, Plus, Trash2, ArrowRight, Check, AlertCircle, FileText, BookOpen } from 'lucide-react';
import { countWords, suggestEvaluationTitle, readFileContent, MAX_FILE_SIZE_BYTES, MAX_SUBMISSION_WORDS } from '../utils/textParser';
import { generateCriteriaAI } from '../utils/gemini';

export default function NewEvaluationPage({ initialData, onEvaluationCreated, apiKey, model }) {
  const [step, setStep] = useState('setup'); // 'setup' | 'rubric'

  // Step 1: Setup State
  const [title, setTitle] = useState(initialData?.title || '');
  const [submissionType, setSubmissionType] = useState('Technical Report');
  const [instructions, setInstructions] = useState('');
  const [contentText, setContentText] = useState(initialData?.contentText || '');
  const [fileName, setFileName] = useState(initialData?.fileName || '');
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Step 2: Rubric Review State
  const [criteria, setCriteria] = useState([]);

  const wordCount = countWords(contentText);
  const isOverLimit = wordCount > MAX_SUBMISSION_WORDS;

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      if (file.size > MAX_FILE_SIZE_BYTES) {
        throw new Error(`File is ${(file.size / (1024 * 1024)).toFixed(1)} MB, exceeding the 10 MB limit.`);
      }

      const text = await readFileContent(file);
      const words = countWords(text);

      if (words > MAX_SUBMISSION_WORDS) {
        throw new Error(`Document contains ${words.toLocaleString()} words, exceeding the ${MAX_SUBMISSION_WORDS.toLocaleString()} word limit.`);
      }

      setFileName(file.name);
      setContentText(text);
      if (!title) {
        setTitle(suggestEvaluationTitle(file.name, text));
      }
      setErrorMsg('');
    } catch (err) {
      setErrorMsg(err.message || 'File read error');
    }
  };

  const handleGenerateAI = async () => {
    if (!title.trim()) {
      setErrorMsg('Please enter an evaluation title.');
      return;
    }
    if (!contentText.trim()) {
      setErrorMsg('Please paste submission content or upload a document.');
      return;
    }
    if (isOverLimit) {
      setErrorMsg(`Submission exceeds the ${MAX_SUBMISSION_WORDS.toLocaleString()} word limit.`);
      return;
    }

    setIsGenerating(true);
    setErrorMsg('');

    try {
      const generated = await generateCriteriaAI({
        title,
        submissionType,
        instructions,
        contentText,
        apiKey,
        model
      });

      if (!generated || generated.length === 0) {
        throw new Error('No criteria could be generated.');
      }

      setCriteria(generated);
      setStep('rubric');
    } catch (err) {
      setErrorMsg(err.message || 'Error generating criteria');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleManualRubric = () => {
    if (!title.trim()) {
      setErrorMsg('Please enter an evaluation title.');
      return;
    }
    if (!contentText.trim()) {
      setErrorMsg('Please paste submission content or upload a document.');
      return;
    }

    setCriteria([
      {
        id: `crit-${Date.now()}-1`,
        name: 'Technical Rigor & Accuracy',
        max_marks: 5,
        description: 'Soundness of arguments, accuracy of logic, and completeness.',
        scoring_guidance: 'Award 4-5 marks for clear methodology with zero critical inaccuracies.'
      },
      {
        id: `crit-${Date.now()}-2`,
        name: 'Clarity & Coherence',
        max_marks: 5,
        description: 'Logical organization, clear documentation, and concise presentation.',
        scoring_guidance: 'Deduct marks for disjointed reasoning or unclear explanations.'
      }
    ]);
    setStep('rubric');
  };

  const handleUpdateCriterion = (idx, field, value) => {
    const updated = [...criteria];
    updated[idx] = { ...updated[idx], [field]: value };
    setCriteria(updated);
  };

  const handleAddCriterion = () => {
    setCriteria([
      ...criteria,
      {
        id: `crit-${Date.now()}-${criteria.length + 1}`,
        name: 'New Evaluation Criterion',
        max_marks: 5,
        description: 'Description of what is being evaluated.',
        scoring_guidance: 'Guide on how to assign marks from 0 to 5.'
      }
    ]);
  };

  const handleDeleteCriterion = (idx) => {
    if (criteria.length <= 1) {
      setErrorMsg('At least one criterion is required.');
      return;
    }
    setCriteria(criteria.filter((_, i) => i !== idx));
  };

  const handleApproveRubric = () => {
    if (criteria.length === 0) {
      setErrorMsg('You must have at least one criterion.');
      return;
    }

    const newEval = {
      id: `eval-${Date.now()}`,
      title: title.trim(),
      submission_type: submissionType,
      instructions: instructions.trim(),
      content_text: contentText,
      word_count: wordCount,
      status: 'pending_human',
      created_at: new Date().toISOString(),
      criteria: criteria.map((c) => ({
        id: c.id || `crit-${Math.random().toString(36).substr(2, 9)}`,
        name: c.name.trim(),
        max_marks: Number(c.max_marks) || 5,
        description: (c.description || '').trim(),
        scoring_guidance: (c.scoring_guidance || '').trim()
      })),
      human_scores: {},
      ai_scores: {}
    };

    onEvaluationCreated(newEval);
  };

  const totalMaxMarks = criteria.reduce((sum, c) => sum + (Number(c.max_marks) || 0), 0);

  return (
    <div>
      {/* Workflow Step Indicator */}
      <div style={{
        background: '#ffffff',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '0.75rem 1.25rem',
        marginBottom: '1.25rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        fontSize: '0.85rem',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <span style={{ fontWeight: step === 'setup' ? 700 : 500, color: step === 'setup' ? 'var(--primary)' : 'var(--text-secondary)' }}>
          1. Submission Details
        </span>
        <span style={{ color: 'var(--text-tertiary)' }}>➔</span>
        <span style={{ fontWeight: step === 'rubric' ? 700 : 500, color: step === 'rubric' ? 'var(--primary)' : 'var(--text-secondary)' }}>
          2. Rubric Review & Calibration
        </span>
        <span style={{ color: 'var(--text-tertiary)' }}>➔</span>
        <span style={{ color: 'var(--text-tertiary)' }}>
          3. Examiner Scoring & AI Comparison
        </span>
      </div>

      {errorMsg && (
        <div className="banner banner-danger" style={{ marginBottom: '1.25rem' }}>
          <AlertCircle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {step === 'setup' && (
        <div className="card">
          <div className="card-title">
            <FileText size={20} color="var(--primary)" />
            Submission Setup
          </div>
          <div className="card-subtitle">
            Provide the submission document and evaluation goals.
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="eval-title">
              Evaluation Title*
            </label>
            <input
              id="eval-title"
              type="text"
              className="form-control"
              placeholder="e.g. Distributed Edge Anomaly Detection or Final Project Audit"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label" htmlFor="eval-type">
                Submission Type
              </label>
              <select
                id="eval-type"
                className="form-control"
                value={submissionType}
                onChange={(e) => setSubmissionType(e.target.value)}
              >
                <option value="Technical Report">Technical Report</option>
                <option value="Written Work">Written Work</option>
                <option value="Code">Code & Scripts</option>
                <option value="Software Project">Software Project</option>
                <option value="Custom">Custom</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                Upload File (Optional)
              </label>
              <label className="btn btn-secondary" style={{ width: '100%', cursor: 'pointer', justifyContent: 'flex-start' }}>
                <BookOpen size={16} color="var(--primary)" />
                <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                  {fileName ? `File: ${fileName}` : 'Choose Document or Code...'}
                </span>
                <input
                  type="file"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                  accept=".txt,.md,.py,.cpp,.h,.hpp,.java,.js,.ts,.json,.html,.css,.sql,.docx,.pdf"
                />
              </label>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="eval-inst">
              Evaluation Instructions (Optional)
            </label>
            <textarea
              id="eval-inst"
              className="form-control"
              rows={2}
              placeholder="e.g. Focus specifically on empirical baseline rigor, edge case handling, and memory constraints."
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
            />
          </div>

          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.375rem' }}>
              <label className="form-label" htmlFor="eval-content" style={{ margin: 0 }}>
                Submission Content*
              </label>
              <span style={{ fontSize: '0.8rem', color: isOverLimit ? 'var(--danger)' : 'var(--text-secondary)' }}>
                {wordCount.toLocaleString()} / {MAX_SUBMISSION_WORDS.toLocaleString()} words
              </span>
            </div>
            <textarea
              id="eval-content"
              className="form-control"
              rows={10}
              placeholder="Paste submission text or code here..."
              value={contentText}
              onChange={(e) => setContentText(e.target.value)}
              required
            />
          </div>

          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
            <button
              className="btn btn-secondary"
              onClick={handleManualRubric}
              disabled={isGenerating || !contentText.trim() || isOverLimit}
            >
              <Edit3 size={16} />
              <span>Create Rubric Manually</span>
            </button>

            <button
              className="btn btn-primary"
              onClick={handleGenerateAI}
              disabled={isGenerating || !contentText.trim() || isOverLimit}
            >
              <Sparkles size={16} />
              <span>{isGenerating ? 'Analyzing with AI...' : 'Analyze Submission with AI'}</span>
            </button>
          </div>
        </div>
      )}

      {step === 'rubric' && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div className="card-title" style={{ margin: 0 }}>
              <Check size={20} color="var(--success)" />
              Review & Customize Rubric
            </div>
            <div className="badge badge-primary" style={{ fontSize: '0.8rem', padding: '0.3rem 0.75rem' }}>
              Total Marks: {totalMaxMarks} pts
            </div>
          </div>
          <div className="card-subtitle">
            Review the proposed evaluation criteria. You can edit names, descriptions, marks, or add custom criteria before approving.
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
            {criteria.map((c, idx) => (
              <div
                key={c.id || idx}
                style={{
                  background: '#ffffff',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1.25rem',
                  boxShadow: 'var(--shadow-sm)'
                }}
              >
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
                  <div style={{ flex: '1 1 280px' }}>
                    <label className="form-label">Criterion Name</label>
                    <input
                      type="text"
                      className="form-control"
                      value={c.name}
                      onChange={(e) => handleUpdateCriterion(idx, 'name', e.target.value)}
                      required
                    />
                  </div>

                  <div style={{ width: '130px' }}>
                    <label className="form-label">Max Marks</label>
                    <input
                      type="number"
                      min={1}
                      max={100}
                      className="form-control"
                      value={c.max_marks}
                      onChange={(e) => handleUpdateCriterion(idx, 'max_marks', Math.max(1, parseInt(e.target.value) || 1))}
                      required
                    />
                  </div>

                  <button
                    className="btn btn-danger btn-sm"
                    style={{ marginTop: '1.75rem' }}
                    onClick={() => handleDeleteCriterion(idx)}
                    title="Delete criterion"
                  >
                    <Trash2 size={15} />
                    <span>Delete</span>
                  </button>
                </div>

                <div className="form-group" style={{ marginBottom: '0.75rem' }}>
                  <label className="form-label">Description</label>
                  <input
                    type="text"
                    className="form-control"
                    value={c.description}
                    onChange={(e) => handleUpdateCriterion(idx, 'description', e.target.value)}
                  />
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Scoring Guidance</label>
                  <input
                    type="text"
                    className="form-control"
                    value={c.scoring_guidance}
                    onChange={(e) => handleUpdateCriterion(idx, 'scoring_guidance', e.target.value)}
                  />
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <button className="btn btn-secondary" onClick={handleAddCriterion}>
              <Plus size={16} />
              <span>Add Another Criterion</span>
            </button>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="btn btn-secondary" onClick={() => setStep('setup')}>
                <span>Back to Setup</span>
              </button>
              <button className="btn btn-success" onClick={handleApproveRubric}>
                <Check size={16} />
                <span>Approve Rubric & Begin Evaluation</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
