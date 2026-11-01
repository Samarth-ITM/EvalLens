"""
Database access and initialization for EvalLens.

Provides safe SQLite connection handling, parameterized queries, schema setup,
migrations, and persistence for evaluations, rubrics, human scores, and AI scores.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from config.settings import settings

SCHEMA_FILE: Path = Path(__file__).resolve().parent / "schema.sql"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.
    Enables foreign key enforcement and row factory access.
    """
    target_path = db_path or settings.db_path
    target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(target_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def _migrate_columns_if_missing(conn: sqlite3.Connection) -> None:
    """
    Safely ensure new columns are added to existing databases without data loss.
    """
    cursor = conn.cursor()

    # Columns in 'evaluations'
    eval_cols = {row["name"] for row in cursor.execute("PRAGMA table_info(evaluations);").fetchall()}
    if "submission_type" not in eval_cols and "evaluations" in eval_cols:
        cursor.execute("ALTER TABLE evaluations ADD COLUMN submission_type TEXT NOT NULL DEFAULT 'Custom';")
    if "instructions" not in eval_cols and "evaluations" in eval_cols:
        cursor.execute("ALTER TABLE evaluations ADD COLUMN instructions TEXT;")
    if "reference_material" not in eval_cols and "evaluations" in eval_cols:
        cursor.execute("ALTER TABLE evaluations ADD COLUMN reference_material TEXT;")
    if "prompt_version" not in eval_cols and "evaluations" in eval_cols:
        cursor.execute("ALTER TABLE evaluations ADD COLUMN prompt_version TEXT DEFAULT 'V3';")
    if "total_words" not in eval_cols and "evaluations" in eval_cols:
        cursor.execute("ALTER TABLE evaluations ADD COLUMN total_words INTEGER DEFAULT 0;")

    # Columns in 'submissions'
    sub_cols = {row["name"] for row in cursor.execute("PRAGMA table_info(submissions);").fetchall()}
    if "word_count" not in sub_cols and "submissions" in sub_cols:
        cursor.execute("ALTER TABLE submissions ADD COLUMN word_count INTEGER DEFAULT 0;")
    if "warnings" not in sub_cols and "submissions" in sub_cols:
        cursor.execute("ALTER TABLE submissions ADD COLUMN warnings TEXT;")

    # Columns in 'rubrics'
    rubric_cols = {row["name"] for row in cursor.execute("PRAGMA table_info(rubrics);").fetchall()}
    if "total_marks" not in rubric_cols and "rubrics" in rubric_cols:
        cursor.execute("ALTER TABLE rubrics ADD COLUMN total_marks REAL NOT NULL DEFAULT 0.0;")
    if "is_approved" not in rubric_cols and "rubrics" in rubric_cols:
        cursor.execute("ALTER TABLE rubrics ADD COLUMN is_approved INTEGER NOT NULL DEFAULT 0;")
    if "approved_at" not in rubric_cols and "rubrics" in rubric_cols:
        cursor.execute("ALTER TABLE rubrics ADD COLUMN approved_at TIMESTAMP;")
    if "prompt_version" not in rubric_cols and "rubrics" in rubric_cols:
        cursor.execute("ALTER TABLE rubrics ADD COLUMN prompt_version TEXT DEFAULT 'V3';")

    # Columns in 'rubric_criteria'
    crit_cols = {row["name"] for row in cursor.execute("PRAGMA table_info(rubric_criteria);").fetchall()}
    if "why_it_matters" not in crit_cols and "rubric_criteria" in crit_cols:
        cursor.execute("ALTER TABLE rubric_criteria ADD COLUMN why_it_matters TEXT;")
    if "evidence_guidance" not in crit_cols and "rubric_criteria" in crit_cols:
        cursor.execute("ALTER TABLE rubric_criteria ADD COLUMN evidence_guidance TEXT;")
    if "evidence_excerpt" not in crit_cols and "rubric_criteria" in crit_cols:
        cursor.execute("ALTER TABLE rubric_criteria ADD COLUMN evidence_excerpt TEXT;")
    if "evidence_location" not in crit_cols and "rubric_criteria" in crit_cols:
        cursor.execute("ALTER TABLE rubric_criteria ADD COLUMN evidence_location TEXT;")
    if "scoring_guidance" not in crit_cols and "rubric_criteria" in crit_cols:
        cursor.execute("ALTER TABLE rubric_criteria ADD COLUMN scoring_guidance TEXT;")
    if "is_ai_generated" not in crit_cols and "rubric_criteria" in crit_cols:
        cursor.execute("ALTER TABLE rubric_criteria ADD COLUMN is_ai_generated INTEGER NOT NULL DEFAULT 1;")

    # Columns in 'ai_scores'
    ai_score_cols = {row["name"] for row in cursor.execute("PRAGMA table_info(ai_scores);").fetchall()}
    if "evidence_location" not in ai_score_cols and "ai_scores" in ai_score_cols:
        cursor.execute("ALTER TABLE ai_scores ADD COLUMN evidence_location TEXT;")
    if "uncertainty" not in ai_score_cols and "ai_scores" in ai_score_cols:
        cursor.execute("ALTER TABLE ai_scores ADD COLUMN uncertainty TEXT;")

    conn.commit()


def init_db(db_path: Optional[Path] = None) -> None:
    """
    Initialize SQLite tables using schema.sql and apply schema migrations.
    Safe to execute multiple times (idempotent).
    """
    target_path = db_path or settings.db_path
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found at: {SCHEMA_FILE}")

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_script = f.read()

    with get_connection(target_path) as conn:
        conn.executescript(schema_script)
        _migrate_columns_if_missing(conn)
        conn.commit()


def execute_query(
    query: str,
    params: tuple[Any, ...] | list[Any] = (),
    db_path: Optional[Path] = None,
) -> int:
    """
    Execute a parameterized INSERT, UPDATE, or DELETE query and return the last row ID.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid or 0


def fetch_all(
    query: str,
    params: tuple[Any, ...] | list[Any] = (),
    db_path: Optional[Path] = None,
) -> List[sqlite3.Row]:
    """
    Execute a parameterized SELECT query and return all matching rows.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def fetch_one(
    query: str,
    params: tuple[Any, ...] | list[Any] = (),
    db_path: Optional[Path] = None,
) -> Optional[sqlite3.Row]:
    """
    Execute a parameterized SELECT query and return the first matching row or None.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()


def list_tables(db_path: Optional[Path] = None) -> List[str]:
    """
    Retrieve names of all user tables in the database.
    """
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
    rows = fetch_all(query, db_path=db_path)
    return [row["name"] for row in rows]


# ---------------------------------------------------------
# Evaluation and Submission Operations
# ---------------------------------------------------------

def create_evaluation(
    title: str,
    description: Optional[str] = None,
    submission_type: str = "Custom",
    instructions: Optional[str] = None,
    reference_material: Optional[str] = None,
    prompt_version: str = "V3",
    total_words: int = 0,
    status: str = "draft",
    db_path: Optional[Path] = None,
) -> int:
    """Create a new evaluation record and return its ID."""
    query = """
        INSERT INTO evaluations (
            title, description, submission_type, instructions,
            reference_material, prompt_version, total_words, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """
    return execute_query(
        query,
        (
            title,
            description or "",
            submission_type,
            instructions or "",
            reference_material or "",
            prompt_version,
            total_words,
            status,
        ),
        db_path=db_path,
    )


def update_evaluation_status(
    evaluation_id: int, status: str, db_path: Optional[Path] = None
) -> None:
    """Update status of an evaluation session."""
    query = "UPDATE evaluations SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;"
    execute_query(query, (status, evaluation_id), db_path=db_path)


def get_evaluation(evaluation_id: int, db_path: Optional[Path] = None) -> Optional[sqlite3.Row]:
    """Fetch an evaluation by ID."""
    query = "SELECT * FROM evaluations WHERE id = ?;"
    return fetch_one(query, (evaluation_id,), db_path=db_path)


def add_submission(
    evaluation_id: int,
    title: str,
    content: str,
    file_name: Optional[str] = None,
    file_path: Optional[str] = None,
    file_type: Optional[str] = None,
    word_count: int = 0,
    warnings: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> int:
    """Save an extracted submission record linked to an evaluation."""
    query = """
        INSERT INTO submissions (
            evaluation_id, title, content, file_name,
            file_path, file_type, word_count, warnings
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """
    return execute_query(
        query,
        (
            evaluation_id,
            title,
            content,
            file_name or "",
            file_path or "",
            file_type or "",
            word_count,
            warnings or "",
        ),
        db_path=db_path,
    )


def get_submissions_for_evaluation(
    evaluation_id: int, db_path: Optional[Path] = None
) -> List[sqlite3.Row]:
    """Retrieve all submissions for a given evaluation."""
    query = "SELECT * FROM submissions WHERE evaluation_id = ? ORDER BY id ASC;"
    return fetch_all(query, (evaluation_id,), db_path=db_path)


# ---------------------------------------------------------
# Rubric & Criteria Operations
# ---------------------------------------------------------

def save_ai_criteria_proposals(
    evaluation_id: int,
    criteria: List[Dict[str, Any]],
    prompt_version: str = "V3",
    db_path: Optional[Path] = None,
) -> None:
    """Store raw AI criteria proposals for an evaluation session."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ai_criteria_proposals WHERE evaluation_id = ?;", (evaluation_id,))
        for idx, crit in enumerate(criteria):
            cursor.execute(
                """
                INSERT INTO ai_criteria_proposals (
                    evaluation_id, name, description, why_it_matters,
                    max_marks, evidence_guidance, evidence_excerpt,
                    evidence_location, scoring_guidance, prompt_version, order_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    evaluation_id,
                    crit.get("name", "Untitled"),
                    crit.get("description", ""),
                    crit.get("why_it_matters", ""),
                    float(crit.get("max_marks", 5.0)),
                    crit.get("evidence_guidance", ""),
                    crit.get("evidence_excerpt", ""),
                    crit.get("evidence_location", ""),
                    crit.get("scoring_guidance", ""),
                    prompt_version,
                    crit.get("order_index", idx),
                ),
            )
        conn.commit()


def get_ai_criteria_proposals(
    evaluation_id: int, db_path: Optional[Path] = None
) -> List[sqlite3.Row]:
    """Retrieve original AI proposals for an evaluation."""
    query = """
        SELECT * FROM ai_criteria_proposals 
        WHERE evaluation_id = ? 
        ORDER BY order_index ASC;
    """
    return fetch_all(query, (evaluation_id,), db_path=db_path)


def save_approved_rubric(
    evaluation_id: int,
    title: str,
    description: str,
    criteria: List[Dict[str, Any]],
    total_marks: float,
    prompt_version: str = "V3",
    db_path: Optional[Path] = None,
) -> int:
    """
    Save the human-approved rubric and its criteria inside a single transaction.
    Updates the evaluation status to 'rubric_approved'.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Insert approved rubric
        cursor.execute(
            """
            INSERT INTO rubrics (
                evaluation_id, title, description, status,
                total_marks, is_approved, approved_at, prompt_version
            ) VALUES (?, ?, ?, 'approved', ?, 1, CURRENT_TIMESTAMP, ?);
            """,
            (evaluation_id, title, description, total_marks, prompt_version),
        )
        rubric_id = cursor.lastrowid or 0

        # Insert approved criteria
        for idx, crit in enumerate(criteria):
            cursor.execute(
                """
                INSERT INTO rubric_criteria (
                    rubric_id, name, description, why_it_matters,
                    max_score, weight, evidence_guidance, evidence_excerpt,
                    evidence_location, scoring_guidance, is_ai_generated, order_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    rubric_id,
                    crit.get("name", "Criterion"),
                    crit.get("description", ""),
                    crit.get("why_it_matters", ""),
                    float(crit.get("max_marks", crit.get("max_score", 5.0))),
                    float(crit.get("weight", 1.0)),
                    crit.get("evidence_guidance", ""),
                    crit.get("evidence_excerpt", ""),
                    crit.get("evidence_location", ""),
                    crit.get("scoring_guidance", ""),
                    1 if crit.get("is_ai_generated", True) else 0,
                    idx,
                ),
            )

        # Update evaluation status
        cursor.execute(
            """
            UPDATE evaluations 
            SET status = 'rubric_approved', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?;
            """,
            (evaluation_id,),
        )

        conn.commit()
        return rubric_id


def get_rubric_with_criteria(
    evaluation_id: int, db_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """Retrieve the approved rubric and all associated criteria for an evaluation."""
    rubric_row = fetch_one(
        "SELECT * FROM rubrics WHERE evaluation_id = ? ORDER BY id DESC LIMIT 1;",
        (evaluation_id,),
        db_path=db_path,
    )
    if not rubric_row:
        return None

    rubric_id = rubric_row["id"]
    criteria_rows = fetch_all(
        "SELECT * FROM rubric_criteria WHERE rubric_id = ? ORDER BY order_index ASC;",
        (rubric_id,),
        db_path=db_path,
    )

    return {
        "rubric": dict(rubric_row),
        "criteria": [dict(c) for c in criteria_rows],
    }


# ---------------------------------------------------------
# Human & AI Scoring Persistence (Series 3)
# ---------------------------------------------------------

def save_human_scores(
    evaluation_id: int,
    scores_data: List[Dict[str, Any]],
    evaluator_name: str = "Human Evaluator",
    db_path: Optional[Path] = None,
) -> None:
    """
    Save human evaluation scores inside a single transaction.
    Replaces or inserts scores per criterion without touching AI scores.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for item in scores_data:
            cursor.execute(
                """
                INSERT INTO human_scores (
                    evaluation_id, criterion_id, score, feedback, evaluator_name, updated_at
                ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(evaluation_id, criterion_id) DO UPDATE SET
                    score = excluded.score,
                    feedback = excluded.feedback,
                    evaluator_name = excluded.evaluator_name,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (
                    evaluation_id,
                    item["criterion_id"],
                    float(item["score"]),
                    item.get("feedback", ""),
                    evaluator_name,
                ),
            )

        cursor.execute(
            """
            UPDATE evaluations 
            SET status = CASE 
                WHEN status = 'completed' THEN 'completed' 
                ELSE 'human_evaluated' 
            END,
            updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?;
            """,
            (evaluation_id,),
        )
        conn.commit()


def get_human_scores(
    evaluation_id: int, db_path: Optional[Path] = None
) -> List[sqlite3.Row]:
    """Retrieve all human scores for an evaluation."""
    query = """
        SELECT hs.*, rc.name as criterion_name, rc.max_score, rc.order_index
        FROM human_scores hs
        JOIN rubric_criteria rc ON hs.criterion_id = rc.id
        WHERE hs.evaluation_id = ?
        ORDER BY rc.order_index ASC;
    """
    return fetch_all(query, (evaluation_id,), db_path=db_path)


def has_human_scores(evaluation_id: int, db_path: Optional[Path] = None) -> bool:
    """Check whether a human evaluation has been submitted for this session."""
    query = "SELECT COUNT(*) as count FROM human_scores WHERE evaluation_id = ?;"
    row = fetch_one(query, (evaluation_id,), db_path=db_path)
    return bool(row and row["count"] > 0)


def save_ai_scores(
    evaluation_id: int,
    ai_scores_data: List[Dict[str, Any]],
    model_name: str,
    db_path: Optional[Path] = None,
) -> None:
    """
    Save AI evaluation scores inside a single transaction.
    Does NOT touch or overwrite human scores.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for item in ai_scores_data:
            cursor.execute(
                """
                INSERT INTO ai_scores (
                    evaluation_id, criterion_id, score, reasoning, evidence_text,
                    evidence_location, uncertainty, model_name, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(evaluation_id, criterion_id, model_name) DO UPDATE SET
                    score = excluded.score,
                    reasoning = excluded.reasoning,
                    evidence_text = excluded.evidence_text,
                    evidence_location = excluded.evidence_location,
                    uncertainty = excluded.uncertainty,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (
                    evaluation_id,
                    item["criterion_id"],
                    float(item["score"]),
                    item.get("reasoning", ""),
                    item.get("evidence_text", item.get("evidence_excerpt", "")),
                    item.get("evidence_location", ""),
                    item.get("uncertainty", ""),
                    model_name,
                ),
            )

        cursor.execute(
            """
            UPDATE evaluations 
            SET status = 'completed', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?;
            """,
            (evaluation_id,),
        )
        conn.commit()


def get_ai_scores(
    evaluation_id: int, model_name: Optional[str] = None, db_path: Optional[Path] = None
) -> List[sqlite3.Row]:
    """Retrieve all AI scores for an evaluation."""
    if model_name:
        query = """
            SELECT ais.*, rc.name as criterion_name, rc.max_score, rc.order_index
            FROM ai_scores ais
            JOIN rubric_criteria rc ON ais.criterion_id = rc.id
            WHERE ais.evaluation_id = ? AND ais.model_name = ?
            ORDER BY rc.order_index ASC;
        """
        return fetch_all(query, (evaluation_id, model_name), db_path=db_path)
    else:
        query = """
            SELECT ais.*, rc.name as criterion_name, rc.max_score, rc.order_index
            FROM ai_scores ais
            JOIN rubric_criteria rc ON ais.criterion_id = rc.id
            WHERE ais.evaluation_id = ?
            ORDER BY rc.order_index ASC, ais.id DESC;
        """
        return fetch_all(query, (evaluation_id,), db_path=db_path)


def has_ai_scores(evaluation_id: int, db_path: Optional[Path] = None) -> bool:
    """Check whether AI scores exist for this evaluation."""
    query = "SELECT COUNT(*) as count FROM ai_scores WHERE evaluation_id = ?;"
    row = fetch_one(query, (evaluation_id,), db_path=db_path)
    return bool(row and row["count"] > 0)


def get_evaluations_summary(db_path: Optional[Path] = None) -> List[sqlite3.Row]:
    """Retrieve summary of all evaluations in descending creation order with scores."""
    query = """
        SELECT 
            e.id,
            e.title,
            e.description,
            e.submission_type,
            e.status,
            e.total_words,
            e.prompt_version,
            e.created_at,
            e.updated_at,
            (SELECT COUNT(*) FROM submissions s WHERE s.evaluation_id = e.id) as submission_count,
            (SELECT total_marks FROM rubrics r WHERE r.evaluation_id = e.id AND r.is_approved = 1 LIMIT 1) as approved_total_marks,
            (SELECT SUM(score) FROM human_scores hs WHERE hs.evaluation_id = e.id) as human_total_score,
            (SELECT SUM(score) FROM ai_scores ais WHERE ais.evaluation_id = e.id) as ai_total_score
        FROM evaluations e
        ORDER BY e.created_at DESC;
    """
    return fetch_all(query, db_path=db_path)
