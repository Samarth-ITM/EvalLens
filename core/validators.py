"""
Data validation models using Pydantic.

Validates application entities, evaluation schemas, criteria proposals, and API key configurations.
"""

from __future__ import annotations

import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

MAX_SUBMISSION_WORDS: int = 5000
MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

ALLOWED_SUBMISSION_TYPES = [
    "Written Work",
    "Code",
    "Software Project",
    "Technical Report",
    "Custom",
]


class APIKeyValidation(BaseModel):
    """Validation for user-provided Gemini API keys."""

    key: str = Field(..., min_length=10, max_length=256, description="Gemini API Key")

    @field_validator("key")
    @classmethod
    def validate_key_format(cls, v: str) -> str:
        clean_key = v.strip()
        if not clean_key:
            raise ValueError("API key cannot be empty or solely whitespace.")
        if re.search(r"\s", clean_key):
            raise ValueError("API key contains invalid whitespace characters.")
        return clean_key


class EvaluationCreate(BaseModel):
    """Validation for creating a new evaluation session."""

    title: str = Field(..., min_length=1, max_length=200, description="Title of the evaluation")
    submission_type: str = Field(default="Custom")
    description: Optional[str] = Field(None, max_length=2000, description="Optional description")
    instructions: Optional[str] = Field(None, max_length=10000, description="Optional evaluation instructions")
    reference_material: Optional[str] = Field(None, max_length=20000, description="Optional reference material")
    prompt_version: str = Field(default="V3", pattern="^(V1|V2|V3)$")
    status: str = Field(default="draft", pattern="^(draft|rubric_proposed|rubric_approved|completed)$")

    @field_validator("submission_type")
    @classmethod
    def validate_submission_type(cls, v: str) -> str:
        if v not in ALLOWED_SUBMISSION_TYPES:
            raise ValueError(f"Submission type must be one of {ALLOWED_SUBMISSION_TYPES}")
        return v


class CriterionProposal(BaseModel):
    """Schema for individual evaluation criteria proposed by AI or edited by humans."""

    name: str = Field(..., min_length=1, max_length=150, description="Criterion name")
    description: str = Field(..., min_length=1, max_length=2000, description="Description of criteria")
    why_it_matters: str = Field(default="", max_length=2000, description="Why this criterion matters")
    max_marks: float = Field(default=5.0, gt=0.0, le=100.0, description="Maximum marks")
    evidence_guidance: str = Field(default="", max_length=2000, description="What evidence to inspect")
    evidence_excerpt: str = Field(default="", max_length=3000, description="Evidence excerpt from submission")
    evidence_location: Optional[str] = Field(default="", max_length=500, description="Page or line location")
    scoring_guidance: str = Field(default="", max_length=2000, description="Scoring guidance")
    order_index: int = Field(default=0, ge=0)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("Criterion name cannot be empty.")
        return v_clean


class CriteriaProposalResponse(BaseModel):
    """Structured response schema returned by Gemini criteria generation."""

    criteria: List[CriterionProposal] = Field(..., min_length=1, description="List of proposed criteria")
    limitation_note: Optional[str] = Field(
        default=None,
        description="Explanation if information was insufficient or partial",
    )
    prompt_version: str = Field(default="V3")

    @field_validator("criteria")
    @classmethod
    def validate_and_deduplicate_criteria(cls, v: List[CriterionProposal]) -> List[CriterionProposal]:
        seen = set()
        deduped = []
        for crit in v:
            key = crit.name.lower().strip()
            if key not in seen:
                seen.add(key)
                deduped.append(crit)
        if not deduped:
            raise ValueError("At least one unique criterion is required.")
        return deduped


class RubricCriterionCreate(BaseModel):
    """Validation for individual rubric criteria during database insert."""

    name: str = Field(..., min_length=1, max_length=150)
    description: str = Field(..., min_length=1, max_length=2000)
    why_it_matters: Optional[str] = Field(default="", max_length=2000)
    max_score: float = Field(default=5.0, gt=0.0, le=100.0)
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    evidence_guidance: Optional[str] = Field(default="", max_length=2000)
    evidence_excerpt: Optional[str] = Field(default="", max_length=3000)
    evidence_location: Optional[str] = Field(default="", max_length=500)
    scoring_guidance: Optional[str] = Field(default="", max_length=2000)
    is_ai_generated: bool = Field(default=True)
    order_index: int = Field(default=0, ge=0)


class ScoreInput(BaseModel):
    """Validation for numerical scores and associated remarks."""

    score: float = Field(..., ge=0.0)
    feedback_or_reasoning: Optional[str] = Field(None, max_length=5000)
