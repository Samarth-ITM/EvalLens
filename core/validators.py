"""
Data validation models using Pydantic.

Validates application entities, evaluation schemas, and API key configurations.
"""

from __future__ import annotations

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class APIKeyValidation(BaseModel):
    """Validation for user-provided Gemini API keys."""

    key: str = Field(..., min_length=10, max_length=256, description="Gemini API Key")

    @field_validator("key")
    @classmethod
    def validate_key_format(cls, v: str) -> str:
        clean_key = v.strip()
        if not clean_key:
            raise ValueError("API key cannot be empty or solely whitespace.")
        # Ensure no invalid characters like spaces or newlines
        if re.search(r"\s", clean_key):
            raise ValueError("API key contains invalid whitespace characters.")
        return clean_key


class EvaluationCreate(BaseModel):
    """Validation for creating a new evaluation session."""

    title: str = Field(..., min_length=1, max_length=200, description="Title of the evaluation")
    description: Optional[str] = Field(None, max_length=2000, description="Optional description")
    status: str = Field(default="draft", pattern="^(draft|in_progress|completed)$")


class RubricCriterionCreate(BaseModel):
    """Validation for individual evaluation criteria."""

    name: str = Field(..., min_length=1, max_length=150)
    description: str = Field(..., min_length=1, max_length=2000)
    max_score: float = Field(default=10.0, gt=0.0, le=100.0)
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    order_index: int = Field(default=0, ge=0)


class ScoreInput(BaseModel):
    """Validation for numerical scores and associated remarks."""

    score: float = Field(..., ge=0.0)
    feedback_or_reasoning: Optional[str] = Field(None, max_length=5000)

