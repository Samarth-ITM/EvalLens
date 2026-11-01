-- EvalLens Initial SQLite Schema (Series 1 Foundation)
-- Manages evaluations, submissions, rubrics, criteria, and separate human/AI scores.
-- No API keys or credentials are ever stored in this database.

PRAGMA foreign_keys = ON;

-- Core Evaluation Sessions
CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'in_progress', 'completed'
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
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE
);

-- Rubric Definitions
CREATE TABLE IF NOT EXISTS rubrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'proposed', 'approved'
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE
);

-- Individual Rubric Criteria
CREATE TABLE IF NOT EXISTS rubric_criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rubric_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    max_score REAL NOT NULL DEFAULT 10.0,
    weight REAL NOT NULL DEFAULT 1.0,
    order_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rubric_id) REFERENCES rubrics(id) ON DELETE CASCADE
);

-- Human Evaluation Scores (Kept strictly separate from AI scores)
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

-- AI Evaluation Scores (Kept strictly separate from Human scores)
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
CREATE INDEX IF NOT EXISTS idx_rubrics_eval_id ON rubrics(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_rubric_criteria_rubric_id ON rubric_criteria(rubric_id);
CREATE INDEX IF NOT EXISTS idx_human_scores_eval_id ON human_scores(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_ai_scores_eval_id ON ai_scores(evaluation_id);

