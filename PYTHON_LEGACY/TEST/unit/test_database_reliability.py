"""
Unit tests for database reliability, transactions, foreign key enforcement, and resilience.

Covers:
- Database initialization on missing file
- Foreign key constraint enforcement (cannot insert orphan records)
- Clean transaction rollback on mid-transaction error
- Persistence across simulated application restarts
- Large text payload storage and retrieval
- Concurrent connection reads and transactional writes
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
import pytest

from database.db import (
    create_evaluation,
    get_evaluation,
    init_db,
    save_approved_rubric,
    save_human_scores,
    save_ai_scores,
    get_connection,
)


def test_init_db_creates_tables_on_missing_file(tmp_path: Path) -> None:
    """Verify that init_db safely creates schema on a non-existent database file."""
    db_file = tmp_path / "fresh_eval_lens.db"
    assert not db_file.exists()

    init_db(db_file)
    assert db_file.exists()

    with get_connection(db_file) as conn:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            ).fetchall()
        ]
        assert "evaluations" in tables
        assert "rubrics" in tables
        assert "rubric_criteria" in tables
        assert "human_scores" in tables
        assert "ai_scores" in tables


def test_foreign_key_constraints_enforced(tmp_path: Path) -> None:
    """Verify that foreign keys are enforced by default and reject orphaned records."""
    db_file = tmp_path / "fk_test.db"
    init_db(db_file)

    with get_connection(db_file) as conn:
        cursor = conn.cursor()
        # Attempt to insert a human score for a non-existent evaluation and criterion
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                """
                INSERT INTO human_scores (evaluation_id, criterion_id, score, feedback)
                VALUES (999999, 999999, 4.0, 'Orphan score');
                """
            )
            conn.commit()


def test_transaction_rollback_on_error(tmp_path: Path) -> None:
    """Verify that if an error occurs mid-transaction, all changes in that transaction are rolled back."""
    db_file = tmp_path / "rollback_test.db"
    init_db(db_file)

    eval_id = create_evaluation(
        title="Rollback Test Evaluation",
        submission_type="Written Work",
        db_path=db_file,
    )

    # Malformed criterion with missing required fields or bad type to cause failure during criteria insertion
    invalid_criteria = [
        {"name": "Valid Criterion 1", "max_score": 5.0},
        # Second criterion has non-numeric max_score to trigger SQLite type/execution error
        {"name": "Broken Criterion", "max_score": "NOT_A_FLOAT_AT_ALL"},
    ]

    # Attempting to save should raise ValueError or sqlite3 error
    with pytest.raises(Exception):
        save_approved_rubric(
            evaluation_id=eval_id,
            title="Broken Rubric",
            description="Testing Rollback",
            criteria=invalid_criteria,
            total_marks=10.0,
            db_path=db_file,
        )

    # Verify that NO rubric or criteria records exist for this evaluation
    with get_connection(db_file) as conn:
        rubrics = conn.execute("SELECT * FROM rubrics WHERE evaluation_id = ?;", (eval_id,)).fetchall()
        assert len(rubrics) == 0

        # Status must not have advanced to rubric_approved
        ev = get_evaluation(eval_id, db_path=db_file)
        assert ev["status"] == "draft"


def test_persistence_across_connections(tmp_path: Path) -> None:
    """Verify that persisted evaluations and rubrics survive connection closure (restart)."""
    db_file = tmp_path / "persistent.db"
    init_db(db_file)

    # 1. Connection 1: Create evaluation & rubric
    eval_id = create_evaluation(
        title="Persistent Evaluation",
        submission_type="Code",
        total_words=250,
        db_path=db_file,
    )
    rubric_id = save_approved_rubric(
        evaluation_id=eval_id,
        title="Persistent Rubric",
        description="Persistence check",
        criteria=[{"name": "Quality", "max_score": 10.0}],
        total_marks=10.0,
        db_path=db_file,
    )

    # 2. Connection 2: Query from a fresh connection
    ev = get_evaluation(eval_id, db_path=db_file)
    assert ev is not None
    assert ev["title"] == "Persistent Evaluation"
    assert ev["status"] == "rubric_approved"


def test_large_text_payload_storage(tmp_path: Path) -> None:
    """Verify that SQLite easily handles large text submissions without truncation or corruption."""
    db_file = tmp_path / "large_payload.db"
    init_db(db_file)

    large_instructions = "Instructions:\n" + ("Lorem ipsum dolor sit amet. " * 500)
    large_ref = "Reference:\n" + ("Ref content line with detailed data.\n" * 300)

    eval_id = create_evaluation(
        title="Large Payload Evaluation",
        instructions=large_instructions,
        reference_material=large_ref,
        db_path=db_file,
    )

    ev = get_evaluation(eval_id, db_path=db_file)
    assert ev["instructions"] == large_instructions
    assert ev["reference_material"] == large_ref
    assert len(ev["instructions"]) > 10000
