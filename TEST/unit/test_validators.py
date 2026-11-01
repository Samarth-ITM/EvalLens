"""
Unit tests for Pydantic validators.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from core.validators import APIKeyValidation, EvaluationCreate, RubricCriterionCreate, ScoreInput


def test_api_key_validator_valid() -> None:
    """Verify validation passes for clean key."""
    val = APIKeyValidation(key="AIzaSyValidFormatKey123456789")
    assert val.key == "AIzaSyValidFormatKey123456789"


def test_api_key_validator_rejects_whitespace() -> None:
    """Verify validation fails if key contains internal spaces."""
    with pytest.raises(ValidationError):
        APIKeyValidation(key="AIzaSy Invalid Key")


def test_evaluation_create_validation() -> None:
    """Verify evaluation creation data validation."""
    eval_item = EvaluationCreate(title="Test Code Review", description="Sample description")
    assert eval_item.title == "Test Code Review"
    assert eval_item.status == "draft"

    with pytest.raises(ValidationError):
        EvaluationCreate(title="")  # Empty title prohibited


def test_rubric_criterion_validation() -> None:
    """Verify criterion validation rules."""
    crit = RubricCriterionCreate(
        name="Clarity",
        description="Assesses how clear the writing is",
        max_score=10.0,
        weight=1.5,
    )
    assert crit.max_score == 10.0
    assert crit.weight == 1.5

    with pytest.raises(ValidationError):
        RubricCriterionCreate(name="Invalid", description="test", max_score=-5.0)

