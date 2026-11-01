"""
Unit tests for application configuration and path handling.
Verifies Requirement 1: Configuration loads correctly.
"""

from __future__ import annotations

from pathlib import Path
from config.settings import Settings, settings, BASE_DIR, DATA_DIR, UPLOADS_DIR


def test_base_dir_resolution() -> None:
    """Verify BASE_DIR resolves correctly to the project root containing app.py."""
    assert BASE_DIR.exists()
    assert (BASE_DIR / "app.py").exists()
    assert (BASE_DIR / "config").exists()


def test_directories_creation() -> None:
    """Verify DATA_DIR and UPLOADS_DIR are created and accessible."""
    assert DATA_DIR.exists()
    assert DATA_DIR.is_dir()
    assert UPLOADS_DIR.exists()
    assert UPLOADS_DIR.is_dir()


def test_settings_initialization() -> None:
    """Verify settings properties load defaults as expected."""
    app_settings = Settings()
    assert app_settings.PROJECT_NAME == "EvalLens"
    assert app_settings.PROJECT_TAGLINE == "Human + AI Evaluation Workspace"
    assert len(app_settings.SUPPORTED_MODELS) >= 3
    assert "gemini-3.5-flash-lite" in app_settings.SUPPORTED_MODELS
    assert app_settings.DEFAULT_MODEL == "gemini-3.5-flash-lite"


def test_settings_security_repr() -> None:
    """Verify __repr__ does not reveal raw API keys."""
    app_settings = Settings()
    repr_str = repr(app_settings)
    assert "Settings(" in repr_str
    assert "AIza" not in repr_str

