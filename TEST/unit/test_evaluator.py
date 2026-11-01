"""
Unit tests for core/evaluator.py.

Verifies:
- Human score validation (bounds, negative scores, exceeding max marks, decimal increments)
- AI prompt construction using only approved criteria
- AI score parsing and validation against criterion maximums
- Clamping/validation of AI scores exceeding rubric maximum
- Malformed AI response handling
- Independence Rule enforcement: AI scores remain hidden until human evaluation is submitted
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest

from core.evaluator import (
    build_ai_scoring_prompt,
    get_visible_ai_scores_for_review,
    parse_and_validate_ai_response,
    validate_human_score,
)
from database.db import init_db, save_human_scores, save_ai_scores


def test_validate_human_score_boundaries() -> None:
    """Verify human score boundary validation."""
    # Valid scores
    assert validate_human_score(0.0, 5.0) == 0.0
    assert validate_human_score(2.5, 5.0) == 2.5
    assert validate_human_score(5.0, 5.0) == 5.0

    # Negative score rejected
    with pytest.raises(ValueError) as excinfo:
        validate_human_score(-0.5, 5.0, "Clarity")
    assert "cannot be negative" in str(excinfo.value)

    # Score exceeding maximum rejected
    with pytest.raises(ValueError) as excinfo:
        validate_human_score(5.5, 5.0, "Clarity")
    assert "cannot exceed the maximum of 5.0 marks" in str(excinfo.value)


def test_build_ai_scoring_prompt() -> None:
    """Verify AI scoring prompt incorporates exact approved criteria and instructions."""
    criteria = [
        {
            "id": 1,
            "name": "Modularity",
            "description": "Functions must be modular",
            "max_score": 5.0,
            "evidence_guidance": "Check function lengths",
            "scoring_guidance": "5 for clean modularity",
        }
    ]
    prompt = build_ai_scoring_prompt(
        submission_text="def test(): pass",
        submission_type="Code",
        instructions="Adhere to PEP8",
        criteria=criteria,
    )

    assert "Modularity" in prompt
    assert "Maximum Marks: 5.0" in prompt
    assert "Adhere to PEP8" in prompt
    assert "You MUST evaluate every single criterion" in prompt
    assert "NEVER invent or hallucinate evidence" in prompt


def test_parse_and_validate_ai_response_valid() -> None:
    """Verify parsing and validation of well-formed AI evaluation responses."""
    criteria = [
        {"id": 1, "name": "Clarity", "max_score": 5.0},
        {"id": 2, "name": "Efficiency", "max_score": 5.0},
    ]
    raw_json = json.dumps(
        {
            "scores": [
                {
                    "criterion_id": 1,
                    "criterion_name": "Clarity",
                    "score": 4.5,
                    "max_marks": 5.0,
                    "reasoning": "Clear structure and prose.",
                    "evidence_text": "Introduction section",
                    "evidence_location": "Page 1",
                    "uncertainty": "",
                },
                {
                    "criterion_id": 2,
                    "criterion_name": "Efficiency",
                    "score": 4.0,
                    "max_marks": 5.0,
                    "reasoning": "Fast algorithm.",
                    "evidence_text": "Binary search loop",
                    "evidence_location": "L24",
                },
            ],
            "overall_reasoning": "Strong submission overall.",
        }
    )

    scores = parse_and_validate_ai_response(raw_json, criteria, "gemini-3.8-flash")
    assert len(scores) == 2
    assert scores[0]["criterion_id"] == 1
    assert scores[0]["score"] == 4.5
    assert scores[1]["score"] == 4.0


def test_parse_ai_response_clamps_exceeding_scores() -> None:
    """Verify that if Gemini returns a score exceeding criterion maximum, it is clamped safely."""
    criteria = [{"id": 1, "name": "Security", "max_score": 5.0}]
    raw_json = json.dumps(
        {
            "scores": [
                {
                    "criterion_id": 1,
                    "criterion_name": "Security",
                    "score": 8.0,  # Exceeds max 5.0
                    "max_marks": 5.0,
                    "reasoning": "Outstanding",
                }
            ]
        }
    )

    scores = parse_and_validate_ai_response(raw_json, criteria, "gemini-3.8-flash")
    assert len(scores) == 1
    assert scores[0]["score"] == 5.0  # Clamped to max_score


def test_parse_ai_response_rejects_malformed_json() -> None:
    """Verify that non-JSON responses from Gemini raise ValueError."""
    criteria = [{"id": 1, "name": "Security", "max_score": 5.0}]
    with pytest.raises(ValueError) as excinfo:
        parse_and_validate_ai_response("Sorry, I cannot help with that.", criteria, "gemini-3.8-flash")
    assert "Gemini returned an invalid JSON response" in str(excinfo.value)


def test_independence_rule_ai_scores_hidden_before_human_submission(tmp_path: Path) -> None:
    """
    CRITICAL INDEPENDENCE RULE:
    The human must not see AI scores or recommendations while entering their own marks.
    get_visible_ai_scores_for_review must return None until human evaluation is recorded.
    """
    from database.db import create_evaluation, save_approved_rubric, get_rubric_with_criteria

    db_file = tmp_path / "test_independence.db"
    init_db(db_file)

    eval_id = create_evaluation(title="Independence Test", db_path=db_file)
    save_approved_rubric(
        evaluation_id=eval_id,
        title="Test Rubric",
        description="",
        criteria=[{"name": "Criterion 1", "max_score": 5.0}],
        total_marks=5.0,
        db_path=db_file,
    )
    rubric_info = get_rubric_with_criteria(eval_id, db_path=db_file)
    crit_id = rubric_info["criteria"][0]["id"]

    # Save AI scores first (e.g. background run)
    save_ai_scores(
        evaluation_id=eval_id,
        ai_scores_data=[{"criterion_id": crit_id, "score": 4.5, "reasoning": "AI thoughts"}],
        model_name="gemini-3.8-flash",
        db_path=db_file,
    )

    # Human has NOT submitted yet -> AI scores MUST be hidden
    visible_before = get_visible_ai_scores_for_review(eval_id, db_path=db_file)
    assert visible_before is None, "AI scores must be hidden before human submission!"

    # Human submits scores
    save_human_scores(
        evaluation_id=eval_id,
        scores_data=[{"criterion_id": crit_id, "score": 4.0, "feedback": "Human comments"}],
        evaluator_name="Human Reviewer",
        db_path=db_file,
    )

    # Now AI scores are unhidden and visible for comparison
    visible_after = get_visible_ai_scores_for_review(eval_id, db_path=db_file)
    assert visible_after is not None
    assert len(visible_after) == 1
    assert visible_after[0]["score"] == 4.5
