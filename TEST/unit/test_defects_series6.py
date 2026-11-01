"""
Unit tests for defects discovered and resolved during Series 6 production verification.
1. ui.pages.new_evaluation: NameError on CriteriaProposalResponse import.
2. database.db: _migrate_columns_if_missing table name check error in ALTER TABLE conditions.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from core.rubric import EditableCriterion, EditableRubric
from core.validators import CriteriaProposalResponse, CriterionProposal
from database.db import _migrate_columns_if_missing, init_db, get_connection


def test_new_evaluation_imports_and_types_accessible() -> None:
    """Verify that CriteriaProposalResponse and CriterionProposal are imported in new_evaluation."""
    from ui.pages import new_evaluation

    assert hasattr(new_evaluation, "CriteriaProposalResponse")
    assert hasattr(new_evaluation, "CriterionProposal")
    assert new_evaluation.CriteriaProposalResponse is CriteriaProposalResponse
    assert new_evaluation.CriterionProposal is CriterionProposal


def test_schema_migration_adds_missing_columns_to_legacy_tables() -> None:
    """
    Verify that _migrate_columns_if_missing correctly detects and adds missing columns
    to a legacy database that lacked Series 2/3 columns.
    """
    with TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "legacy_test.db"

        # Create a legacy evaluations table without submission_type, instructions, etc.
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(
            """
            CREATE TABLE evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()

        # Run migration on legacy table
        _migrate_columns_if_missing(conn)

        # Verify new columns exist
        cursor = conn.cursor()
        cols = {row[1] for row in cursor.execute("PRAGMA table_info(evaluations);").fetchall()}
        assert "submission_type" in cols
        assert "instructions" in cols
        assert "reference_material" in cols
        assert "prompt_version" in cols
        assert "total_words" in cols

        conn.close()

