"""
Unit tests for comparison mathematics, statistical edge cases, and numerical boundary conditions.

Covers:
- Perfect agreement (human == AI across all criteria)
- Complete disagreement (maximum divergence across all criteria)
- Fractional scores (0.5 steps, unequal denominators)
- Rubrics with unequal criteria maximum marks (e.g., 5, 10, 20)
- Single-criterion rubrics
- Zero scores (human=0, AI=0)
- All maximum scores (human=max, AI=max)
- Mathematical correctness of MAE: sum(|H% - A%|) / N
- Pearson correlation graceful handling of zero variance (no division by zero crash)
- Directional bias correct sign (positive when human > AI, negative when AI > human)
- Percentage calculation exactness and boundary precision
"""

from __future__ import annotations

import pytest
from core.comparison import (
    calculate_comparison,
    calculate_normalized_score,
    calculate_pearson_correlation,
)


def test_perfect_agreement_all_metrics() -> None:
    """Verify metrics when human and AI provide identical scores."""
    criteria = [
        {"id": 1, "name": "Crit A", "max_score": 10.0},
        {"id": 2, "name": "Crit B", "max_score": 10.0},
        {"id": 3, "name": "Crit C", "max_score": 10.0},
    ]
    human_scores = [{"criterion_id": 1, "score": 8.0}, {"criterion_id": 2, "score": 6.0}, {"criterion_id": 3, "score": 10.0}]
    ai_scores = [{"criterion_id": 1, "score": 8.0}, {"criterion_id": 2, "score": 6.0}, {"criterion_id": 3, "score": 10.0}]

    summary = calculate_comparison(
        evaluation_id=1,
        evaluation_title="Perfect Agreement",
        criteria=criteria,
        human_scores=human_scores,
        ai_scores=ai_scores,
    )

    assert summary.human_total_marks == 24.0
    assert summary.ai_total_marks == 24.0
    assert summary.max_possible_marks == 30.0
    assert summary.human_percentage == 80.0
    assert summary.ai_percentage == 80.0
    assert summary.total_difference == 0.0
    assert summary.directional_bias == 0.0
    assert summary.mae == 0.0
    assert summary.agreement_percentage == 100.0
    assert summary.correlation == 1.0


def test_complete_disagreement_polar_opposite() -> None:
    """Verify metrics when human awards 100% and AI awards 0% on every criterion."""
    criteria = [
        {"id": 1, "name": "Crit 1", "max_score": 5.0},
        {"id": 2, "name": "Crit 2", "max_score": 5.0},
    ]
    human_scores = [{"criterion_id": 1, "score": 5.0}, {"criterion_id": 2, "score": 5.0}]
    ai_scores = [{"criterion_id": 1, "score": 0.0}, {"criterion_id": 2, "score": 0.0}]

    summary = calculate_comparison(
        evaluation_id=2,
        evaluation_title="Complete Disagreement",
        criteria=criteria,
        human_scores=human_scores,
        ai_scores=ai_scores,
    )

    assert summary.human_total_marks == 10.0
    assert summary.ai_total_marks == 0.0
    assert summary.human_percentage == 100.0
    assert summary.ai_percentage == 0.0
    assert summary.directional_bias == 10.0  # Human is 10 points higher
    assert summary.mae == 100.0  # 100 percentage points error
    assert summary.agreement_percentage == 0.0
    # Zero variance in both lists -> correlation should safely be None without zero division crash
    assert summary.correlation is None


def test_directional_bias_signed_behavior() -> None:
    """Verify that directional bias is positive when human > AI, and negative when AI > human."""
    criteria = [{"id": 1, "name": "Crit 1", "max_score": 10.0}]

    # Case A: Human > AI -> positive bias
    summary_pos = calculate_comparison(
        evaluation_id=3,
        evaluation_title="Positive Bias",
        criteria=criteria,
        human_scores=[{"criterion_id": 1, "score": 8.0}],
        ai_scores=[{"criterion_id": 1, "score": 6.0}],
    )
    assert summary_pos.directional_bias == 2.0
    assert summary_pos.total_difference == 2.0

    # Case B: AI > Human -> negative bias
    summary_neg = calculate_comparison(
        evaluation_id=4,
        evaluation_title="Negative Bias",
        criteria=criteria,
        human_scores=[{"criterion_id": 1, "score": 5.5}],
        ai_scores=[{"criterion_id": 1, "score": 9.0}],
    )
    assert summary_neg.directional_bias == -3.5
    assert summary_neg.total_difference == -3.5


def test_rubrics_with_unequal_criteria_weights() -> None:
    """Verify normalized differences and MAE when criteria have different max scores."""
    criteria = [
        {"id": 1, "name": "Crit Small", "max_score": 4.0},   # 1 pt diff = 25% norm diff
        {"id": 2, "name": "Crit Large", "max_score": 20.0},  # 2 pt diff = 10% norm diff
        {"id": 3, "name": "Crit Medium", "max_score": 10.0}, # 1 pt diff = 10% norm diff
    ]
    human_scores = [
        {"criterion_id": 1, "score": 3.0},   # 75%
        {"criterion_id": 2, "score": 18.0},  # 90%
        {"criterion_id": 3, "score": 8.0},   # 80%
    ]
    ai_scores = [
        {"criterion_id": 1, "score": 2.0},   # 50% -> norm diff = 25%
        {"criterion_id": 2, "score": 16.0},  # 80% -> norm diff = 10%
        {"criterion_id": 3, "score": 7.0},   # 70% -> norm diff = 10%
    ]

    summary = calculate_comparison(
        evaluation_id=5,
        evaluation_title="Unequal Criteria Weights",
        criteria=criteria,
        human_scores=human_scores,
        ai_scores=ai_scores,
        disagreement_threshold=10.0,
    )

    assert summary.max_possible_marks == 34.0
    assert summary.human_total_marks == 29.0
    assert summary.ai_total_marks == 25.0

    # Human percentage: 29 / 34 = 85.29%
    assert summary.human_percentage == 85.29
    # AI percentage: 25 / 34 = 73.53%
    assert summary.ai_percentage == 73.53

    # Criteria differences:
    # Crit 1: |75 - 50| = 25.0
    # Crit 2: |90 - 80| = 10.0
    # Crit 3: |80 - 70| = 10.0
    # MAE = (25.0 + 10.0 + 10.0) / 3 = 45.0 / 3 = 15.00
    assert summary.mae == 15.00
    # Agreement: 2 out of 3 within 10 percentage points = 66.67%
    assert summary.agreement_percentage == 66.67


def test_single_criterion_rubric() -> None:
    """Verify behavior on minimal single-criterion rubric."""
    criteria = [{"id": 1, "name": "Sole Criterion", "max_score": 5.0}]
    human_scores = [{"criterion_id": 1, "score": 4.5}]
    ai_scores = [{"criterion_id": 1, "score": 4.0}]

    summary = calculate_comparison(
        evaluation_id=6,
        evaluation_title="Single Criterion",
        criteria=criteria,
        human_scores=human_scores,
        ai_scores=ai_scores,
    )

    # Human: 4.5/5.0 = 90.0%
    # AI: 4.0/5.0 = 80.0%
    # Norm Diff = 10.0% -> In agreement
    assert summary.mae == 10.0
    assert summary.agreement_percentage == 100.0
    # Single pair -> correlation is undefined (fewer than 2 pairs)
    assert summary.correlation is None


def test_zero_scores_and_all_maximum_scores() -> None:
    """Verify boundary conditions: all zeros and all max scores."""
    criteria = [
        {"id": 1, "name": "Crit A", "max_score": 10.0},
        {"id": 2, "name": "Crit B", "max_score": 10.0},
    ]

    # Both zero
    summary_zeros = calculate_comparison(
        evaluation_id=7,
        evaluation_title="Zeros",
        criteria=criteria,
        human_scores=[{"criterion_id": 1, "score": 0.0}, {"criterion_id": 2, "score": 0.0}],
        ai_scores=[{"criterion_id": 1, "score": 0.0}, {"criterion_id": 2, "score": 0.0}],
    )
    assert summary_zeros.human_total_marks == 0.0
    assert summary_zeros.ai_total_marks == 0.0
    assert summary_zeros.human_percentage == 0.0
    assert summary_zeros.ai_percentage == 0.0
    assert summary_zeros.mae == 0.0
    assert summary_zeros.agreement_percentage == 100.0
    assert summary_zeros.correlation is None  # Zero variance handled safely

    # Both max
    summary_max = calculate_comparison(
        evaluation_id=8,
        evaluation_title="All Max",
        criteria=criteria,
        human_scores=[{"criterion_id": 1, "score": 10.0}, {"criterion_id": 2, "score": 10.0}],
        ai_scores=[{"criterion_id": 1, "score": 10.0}, {"criterion_id": 2, "score": 10.0}],
    )
    assert summary_max.human_total_marks == 20.0
    assert summary_max.ai_total_marks == 20.0
    assert summary_max.human_percentage == 100.0
    assert summary_max.ai_percentage == 100.0
    assert summary_max.mae == 0.0
    assert summary_max.agreement_percentage == 100.0
    assert summary_max.correlation is None  # Zero variance handled safely


def test_pearson_correlation_direct_edge_cases() -> None:
    """Verify calculate_pearson_correlation standalone behavior."""
    # Fewer than 2 items
    assert calculate_pearson_correlation([], []) is None
    assert calculate_pearson_correlation([5.0], [5.0]) is None

    # Mismatched lengths
    assert calculate_pearson_correlation([1.0, 2.0], [1.0]) is None

    # Zero variance in one or both
    assert calculate_pearson_correlation([5.0, 5.0, 5.0], [1.0, 2.0, 3.0]) is None
    assert calculate_pearson_correlation([1.0, 2.0, 3.0], [4.0, 4.0, 4.0]) is None

    # Perfect positive correlation (r = 1.0)
    assert calculate_pearson_correlation([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]) == 1.0

    # Perfect negative correlation (r = -1.0)
    assert calculate_pearson_correlation([1.0, 2.0, 3.0], [6.0, 4.0, 2.0]) == -1.0

    # Moderate correlation
    r = calculate_pearson_correlation([1.0, 2.0, 3.0, 4.0], [1.5, 2.1, 2.9, 4.2])
    assert r is not None and 0.95 <= r <= 1.0

