"""
Shared fixtures and test helpers for EvalLens tests.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator
import pytest
from database.db import init_db


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """Provide a temporary SQLite database path for isolated testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_evallens.db"
        init_db(db_path)
        yield db_path

