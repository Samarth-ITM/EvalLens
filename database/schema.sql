-- EvalLens Database Schema (Series 1 & 2)
-- Manages evaluations, submissions, AI proposals, approved rubrics, criteria, and human/AI scores.
-- No API keys or credentials are ever stored in this database.

PRAGMA foreign_keys = ON;

-- Core Evaluation Sessions
CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    submission_type TEXT NOT NULL DEFAULT 'Custom', -- 'Written Work', 'Code', 'Software Project', 'Technical Report', 'Custom'
    instructions TEXT,
    reference_material TEXT,
    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'rubric_proposed', 'rubric_approved', 'completed'
    prompt_version TEXT DEFAULT 'V3',
    total_words INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Submitted Artifacts or Text
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    file_name TEXT,
    file_path TEXT,
    file_type TEXT,
    word_count INTEGER DEFAULT 0,
    warnings TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE
);

-- AI Criteria Proposals (Keeps initial AI proposals immutable & distinct from human edits)
CREATE TABLE IF NOT EXISTS ai_criteria_proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    why_it_matters TEXT,
    max_marks REAL NOT NULL DEFAULT 5.0,
    evidence_guidance TEXT,
    evidence_excerpt TEXT,
    evidence_location TEXT,
    scoring_guidance TEXT,
    prompt_version TEXT NOT NULL DEFAULT 'V3',
    order_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE
);

-- Rubric Definitions (Approved or active human-reviewed rubrics)
CREATE TABLE IF NOT EXISTS rubrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'proposed', 'approved'
    total_marks REAL NOT NULL DEFAULT 0.0,
    is_approved INTEGER NOT NULL DEFAULT 0,
    approved_at TIMESTAMP,
    prompt_version TEXT DEFAULT 'V3',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE
);

-- Individual Rubric Criteria (Human-approved/edited criteria)
CREATE TABLE IF NOT EXISTS rubric_criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rubric_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    why_it_matters TEXT,
    max_score REAL NOT NULL DEFAULT 5.0,
    weight REAL NOT NULL DEFAULT 1.0,
    evidence_guidance TEXT,
    evidence_excerpt TEXT,
    evidence_location TEXT,
    scoring_guidance TEXT,
    is_ai_generated INTEGER NOT NULL DEFAULT 1,
    order_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rubric_id) REFERENCES rubrics(id) ON DELETE CASCADE
);

-- Human Evaluation Scores (Kept strictly separate from AI scores, reserved for Series 3)
CREATE TABLE IF NOT EXISTS human_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    criterion_id INTEGER NOT NULL,
    score REAL NOT NULL,
    feedback TEXT,
    evaluator_name TEXT DEFAULT 'Human Evaluator',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE,
    FOREIGN KEY (criterion_id) REFERENCES rubric_criteria(id) ON DELETE CASCADE,
    UNIQUE(evaluation_id, criterion_id)
);

-- AI Evaluation Scores (Kept strictly separate from Human scores, reserved for Series 3)
CREATE TABLE IF NOT EXISTS ai_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    criterion_id INTEGER NOT NULL,
    score REAL NOT NULL,
    reasoning TEXT,
    evidence_text TEXT,
    model_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE,
    FOREIGN KEY (criterion_id) REFERENCES rubric_criteria(id) ON DELETE CASCADE,
    UNIQUE(evaluation_id, criterion_id, model_name)
);

-- Indexes for performance and quick foreign key lookups
CREATE INDEX IF NOT EXISTS idx_submissions_eval_id ON submissions(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_ai_criteria_eval_id ON ai_criteria_proposals(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_rubrics_eval_id ON rubrics(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_rubric_criteria_rubric_id ON rubric_criteria(rubric_id);
CREATE INDEX IF NOT EXISTS idx_human_scores_eval_id ON human_scores(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_ai_scores_eval_id ON ai_scores(evaluation_id);
