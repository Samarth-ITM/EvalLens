"""
Database access and initialization for EvalLens.

Provides safe SQLite connection handling, parameterized queries, and schema setup.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, List, Optional
from config.settings import settings

SCHEMA_FILE: Path = Path(__file__).resolve().parent / "schema.sql"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.
    Enables foreign key enforcement and row factory access.
    """
    target_path = db_path or settings.db_path
    # Ensure parent directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(target_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """
    Initialize SQLite tables using schema.sql.
    Safe to execute multiple times (idempotent).
    """
    target_path = db_path or settings.db_path
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found at: {SCHEMA_FILE}")

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_script = f.read()

    with get_connection(target_path) as conn:
        conn.executescript(schema_script)
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


def get_evaluations_summary(db_path: Optional[Path] = None) -> List[sqlite3.Row]:
    """
    Retrieve a summary list of all evaluations in descending creation order.
    """
    query = """
        SELECT 
            id,
            title,
            description,
            status,
            created_at,
            updated_at
        FROM evaluations
        ORDER BY created_at DESC;
    """
    return fetch_all(query, db_path=db_path)

