"""
Unit tests for core/comparison.py.

Verifies:
- Normalized score calculation: (score / max_marks) * 100
- Raw and normalized absolute differences per criterion
- Mean Absolute Error (MAE) using normalized differences
- Agreement percentage calculation (tolerance: 10 percentage points)
- Identification of significant disagreement (> 10 percentage points)
- Missing AI score behavior: missing scores are NOT treated as zero
- Human-only evaluation handling without comparison
- Numerical boundary cases (zero scores, 100% agreement, 100% divergence)
"""

from __future__ import annotations

import pytest
from core.comparison import (
    calculate_comparison,
    calculate_normalized_score,
)


def test_calculate_normalized_score() -> None:
    """Verify (score / max_marks) * 100 calculation."""
    assert calculate_normalized_score(5.0, 5.0) == 100.0
    assert calculate_normalized_score(2.5, 5.0) == 50.0
    assert calculate_normalized_score(0.0, 5.0) == 0.0
    assert calculate_normalized_score(3.0, 10.0) == 30.0
    # Guard against divide by zero
    assert calculate_normalized_score(5.0, 0.0) == 0.0


def test_comparison_calculations_full_agreement() -> None:
    """Verify MAE=0.0 and 100% agreement when human and AI scores match identically."""
    criteria = [
        {"id": 1, "name": "Criterion 1", "max_score": 5.0},
        {"id": 2, "name": "Criterion 2", "max_score": 5.0},
    ]
    human_scores = [
        {"criterion_id": 1, "score": 4.0, "feedback": "Good"},
        {"criterion_id": 2, "score": 5.0, "feedback": "Excellent"},
    ]
    ai_scores = [
        {"criterion_id": 1, "score": 4.0, "reasoning": "Well done"},
        {"criterion_id": 2, "score": 5.0, "reasoning": "Matches rubric"},
    ]

    summary = calculate_comparison(
        evaluation_id=101,
        evaluation_title="Test Evaluation",
        criteria=criteria,
        human_scores=human_scores,
        ai_scores=ai_scores,
    )

    assert summary.has_ai_evaluation is True
    assert summary.human_total_marks == 9.0
    assert summary.ai_total_marks == 9.0
    assert summary.max_possible_marks == 10.0
    assert summary.human_percentage == 90.0
    assert summary.ai_percentage == 90.0
    assert summary.total_difference == 0.0
    assert summary.mae == 0.0
    assert summary.agreement_percentage == 100.0

    for c in summary.criteria_comparisons:
        assert c.absolute_difference == 0.0
        assert c.normalized_difference == 0.0
        assert c.is_in_agreement is True
        assert c.significant_disagreement is False


def test_comparison_calculations_within_and_exceeding_tolerance() -> None:
    """
    Verify agreement threshold (10 percentage points).
    Criterion 1: Human 4.0/5.0 (80%), AI 4.5/5.0 (90%) -> Diff = 10% (In agreement)
    Criterion 2: Human 2.0/5.0 (40%), AI 3.5/5.0 (70%) -> Diff = 30% (Disagreement)
    Criterion 3: Human 5.0/5.0 (100%), AI 4.8/5.0 (96%) -> Diff = 4% (In agreement)
    """
    criteria = [
        {"id": 1, "name": "Clarity", "max_score": 5.0},
        {"id": 2, "name": "Correctness", "max_score": 5.0},
        {"id": 3, "name": "Style", "max_score": 5.0},
    ]
    human_scores = [
        {"criterion_id": 1, "score": 4.0},
        {"criterion_id": 2, "score": 2.0},
        {"criterion_id": 3, "score": 5.0},
    ]
    ai_scores = [
        {"criterion_id": 1, "score": 4.5},
        {"criterion_id": 2, "score": 3.5},
        {"criterion_id": 3, "score": 4.8},
    ]

    summary = calculate_comparison(
        evaluation_id=102,
        evaluation_title="Multi Criteria Comparison",
        criteria=criteria,
        human_scores=human_scores,
        ai_scores=ai_scores,
        disagreement_threshold=10.0,
    )

    assert summary.has_ai_evaluation is True
    assert summary.human_total_marks == 11.0
    assert summary.ai_total_marks == 12.8
    assert summary.max_possible_marks == 15.0

    # Criterion 1: norm_diff = 10.0 -> Agreement
    c1 = summary.criteria_comparisons[0]
    assert c1.human_normalized == 80.0
    assert c1.ai_normalized == 90.0
    assert c1.normalized_difference == 10.0
    assert c1.is_in_agreement is True
    assert c1.significant_disagreement is False

    # Criterion 2: norm_diff = 30.0 -> Disagreement
    c2 = summary.criteria_comparisons[1]
    assert c2.human_normalized == 40.0
    assert c2.ai_normalized == 70.0
    assert c2.normalized_difference == 30.0
    assert c2.is_in_agreement is False
    assert c2.significant_disagreement is True

    # Criterion 3: norm_diff = 4.0 -> Agreement
    c3 = summary.criteria_comparisons[2]
    assert c3.normalized_difference == 4.0
    assert c3.is_in_agreement is True

    # MAE = (10.0 + 30.0 + 4.0) / 3 = 44.0 / 3 = 14.67
    assert summary.mae == pytest.approx(14.67, abs=0.01)

    # Agreement = 2 out of 3 = 66.67%
    assert summary.agreement_percentage == pytest.approx(66.67, abs=0.01)


def test_missing_ai_scores_not_treated_as_zero() -> None:
    """
    CRITICAL REQUIREMENT:
    Handle missing AI scores correctly. Do NOT treat missing scores as zero.
    If Criterion 2 has no AI score, it must be excluded from MAE and Agreement.
    """
    criteria = [
        {"id": 1, "name": "Criterion 1", "max_score": 5.0},
        {"id": 2, "name": "Criterion 2 (Missing AI)", "max_score": 5.0},
        {"id": 3, "name": "Criterion 3", "max_score": 5.0},
    ]
    human_scores = [
        {"criterion_id": 1, "score": 4.0},
        {"criterion_id": 2, "score": 3.0},
        {"criterion_id": 3, "score": 5.0},
    ]
    # AI only scored Criterion 1 and 3
    ai_scores = [
        {"criterion_id": 1, "score": 4.0},  # Diff = 0%
        {"criterion_id": 3, "score": 4.5},  # Diff = 10%
    ]

    summary = calculate_comparison(
        evaluation_id=103,
        evaluation_title="Partial AI Evaluation",
        criteria=criteria,
        human_scores=human_scores,
        ai_scores=ai_scores,
    )

    c2 = summary.criteria_comparisons[1]
    assert c2.human_score == 3.0
    assert c2.ai_score is None
    assert c2.ai_normalized is None
    assert c2.normalized_difference is None
    assert c2.is_in_agreement is None

    # MAE must be calculated ONLY over the 2 evaluated criteria: (0.0 + 10.0) / 2 = 5.0%
    # If criterion 2 had been treated as 0 (diff = 60%), MAE would have been (0 + 60 + 10) / 3 = 23.33%
    assert summary.mae == 5.0
    assert summary.agreement_percentage == 100.0


def test_human_only_evaluation_handling() -> None:
    """
    Verify that if no AI evaluation was performed, human results are returned
    without crashing or faking comparison metrics.
    """
    criteria = [
        {"id": 1, "name": "Essay Content", "max_score": 10.0},
        {"id": 2, "name": "Grammar", "max_score": 10.0},
    ]
    human_scores = [
        {"criterion_id": 1, "score": 8.0, "feedback": "Strong arguments"},
        {"criterion_id": 2, "score": 9.0, "feedback": "Minor typos"},
    ]

    summary = calculate_comparison(
        evaluation_id=104,
        evaluation_title="Human Only Review",
        criteria=criteria,
        human_scores=human_scores,
        ai_scores=None,
    )

    assert summary.has_ai_evaluation is False
    assert summary.human_total_marks == 17.0
    assert summary.max_possible_marks == 20.0
    assert summary.human_percentage == 85.0
    assert summary.ai_total_marks is None
    assert summary.ai_percentage is None
    assert summary.mae is None
    assert summary.agreement_percentage is None
    assert summary.total_difference is None

    for c in summary.criteria_comparisons:
        assert c.ai_score is None
        assert c.normalized_difference is None
        assert c.is_in_agreement is None

