"""
Integration tests for module imports.
Verifies Requirement 4: Application modules can be imported without error.
"""

from __future__ import annotations

import importlib
import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "config.settings",
        "database.db",
        "core.ai_client",
        "core.validators",
        "core.submission",
        "core.document_parser",
        "core.criteria_generator",
        "core.rubric",
        "core.evaluator",
        "core.comparison",
        "ui.components.header",
        "ui.pages.home",
        "ui.pages.new_evaluation",
        "ui.pages.evaluate",
        "ui.pages.history",
        "ui.pages.settings_page",
        "app",
    ],
)
def test_application_modules_import(module_name: str) -> None:
    """Verify that every module defined in the application skeleton imports cleanly."""
    mod = importlib.import_module(module_name)
    assert mod is not None

