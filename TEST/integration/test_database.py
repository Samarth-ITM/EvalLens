"""
Integration tests for SQLite database initialization and schema.
Verifies Requirement 2: Database initializes successfully.
Verifies Requirement 3: Database tables exist.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
import sqlite3
import pytest

from database.db import (
    execute_query,
    fetch_all,
    fetch_one,
    init_db,
    list_tables,
)


@pytest.fixture
def test_db_path() -> Path:
    """Create a temporary database path for testing."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    path = Path(temp_file.name)
    yield path
    if path.exists():
        path.unlink()


def test_database_initialization(test_db_path: Path) -> None:
    """Verify that init_db creates all required tables and indexes."""
    init_db(test_db_path)
    tables = list_tables(test_db_path)

    expected_tables = {
        "evaluations",
        "submissions",
        "rubrics",
        "rubric_criteria",
        "human_scores",
        "ai_scores",
    }
    assert expected_tables.issubset(set(tables)), f"Missing tables: {expected_tables - set(tables)}"


def test_schema_separate_scores(test_db_path: Path) -> None:
    """Verify human_scores and ai_scores exist as distinct tables."""
    init_db(test_db_path)
    tables = list_tables(test_db_path)
    assert "human_scores" in tables
    assert "ai_scores" in tables
    assert "human_scores" != "ai_scores"


def test_idempotent_initialization(test_db_path: Path) -> None:
    """Verify that running init_db multiple times is safe and causes no errors."""
    init_db(test_db_path)
    # Run second time
    init_db(test_db_path)
    tables = list_tables(test_db_path)
    assert "evaluations" in tables


def test_parameterized_query_and_foreign_keys(test_db_path: Path) -> None:
    """Verify parameterized queries and foreign key enforcement."""
    init_db(test_db_path)

    # Insert an evaluation
    eval_id = execute_query(
        "INSERT INTO evaluations (title, description, status) VALUES (?, ?, ?);",
        ("Test Eval 1", "Sample description", "draft"),
        db_path=test_db_path,
    )
    assert eval_id > 0

    # Fetch inserted row
    row = fetch_one(
        "SELECT id, title, status FROM evaluations WHERE id = ?;",
        (eval_id,),
        db_path=test_db_path,
    )
    assert row is not None
    assert row["title"] == "Test Eval 1"
    assert row["status"] == "draft"

    # Test foreign key enforcement: inserting submission with invalid evaluation_id should fail
    with pytest.raises(sqlite3.IntegrityError):
        execute_query(
            "INSERT INTO submissions (evaluation_id, title) VALUES (?, ?);",
            (999999, "Orphan Submission"),
            db_path=test_db_path,
        )

