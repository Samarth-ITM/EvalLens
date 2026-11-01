"""
Score Comparison and Alignment Analytics for EvalLens.

Implements normalized difference, Mean Absolute Error (MAE), and agreement percentage
calculations between human and AI scores.
Handles missing AI evaluations safely without treating absent scores as zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CriterionComparison:
    """Comparison details for a single rubric criterion."""

    criterion_id: int
    criterion_name: str
    max_marks: float
    human_score: float
    human_feedback: str = ""
    ai_score: Optional[float] = None
    ai_reasoning: str = ""
    ai_evidence_excerpt: str = ""
    ai_evidence_location: str = ""
    ai_uncertainty: str = ""
    human_normalized: float = 0.0
    ai_normalized: Optional[float] = None
    absolute_difference: Optional[float] = None
    normalized_difference: Optional[float] = None
    is_in_agreement: Optional[bool] = None
    significant_disagreement: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert criterion comparison to a dictionary."""
        return {
            "criterion_id": self.criterion_id,
            "criterion_name": self.criterion_name,
            "max_marks": self.max_marks,
            "human_score": self.human_score,
            "human_feedback": self.human_feedback,
            "ai_score": self.ai_score,
            "ai_reasoning": self.ai_reasoning,
            "ai_evidence_excerpt": self.ai_evidence_excerpt,
            "ai_evidence_location": self.ai_evidence_location,
            "ai_uncertainty": self.ai_uncertainty,
            "human_normalized": self.human_normalized,
            "ai_normalized": self.ai_normalized,
            "absolute_difference": self.absolute_difference,
            "normalized_difference": self.normalized_difference,
            "is_in_agreement": self.is_in_agreement,
            "significant_disagreement": self.significant_disagreement,
        }


@dataclass
class EvaluationComparisonSummary:
    """Aggregated comparison summary between human evaluation and AI evaluation."""

    evaluation_id: int
    evaluation_title: str
    has_ai_evaluation: bool
    max_possible_marks: float
    human_total_marks: float
    human_percentage: float
    ai_total_marks: Optional[float] = None
    ai_percentage: Optional[float] = None
    total_difference: Optional[float] = None
    mae: Optional[float] = None
    agreement_percentage: Optional[float] = None
    directional_bias: Optional[float] = None
    correlation: Optional[float] = None
    criteria_comparisons: List[CriterionComparison] = field(default_factory=list)


def calculate_pearson_correlation(
    human_scores: List[float],
    ai_scores: List[float],
) -> Optional[float]:
    """
    Calculate Pearson correlation coefficient r between paired scores.
    Handles zero variance gracefully without crashing (division by zero).
    Returns None if:
    - lengths do not match or fewer than 2 pairs
    - zero variance in either series (standard deviation == 0)
    """
    if len(human_scores) != len(ai_scores) or len(human_scores) < 2:
        return None

    n = len(human_scores)
    mean_h = sum(human_scores) / n
    mean_a = sum(ai_scores) / n

    diff_h = [h - mean_h for h in human_scores]
    diff_a = [a - mean_a for a in ai_scores]

    var_h = sum(d * d for d in diff_h)
    var_a = sum(d * d for d in diff_a)

    if var_h <= 1e-9 or var_a <= 1e-9:
        # Zero variance: constant scores, correlation undefined
        return None

    cov = sum(dh * da for dh, da in zip(diff_h, diff_a))
    r = cov / ((var_h * var_a) ** 0.5)
    r_clamped = max(-1.0, min(1.0, float(r)))
    return round(r_clamped, 4)


def calculate_normalized_score(score: float, max_marks: float) -> float:
    """
    Calculate normalized percentage score: (score / max_marks) * 100.
    """
    if max_marks <= 0.0:
        return 0.0
    return round((score / max_marks) * 100.0, 2)


def calculate_comparison(
    evaluation_id: int,
    evaluation_title: str,
    criteria: List[Dict[str, Any]],
    human_scores: List[Dict[str, Any]],
    ai_scores: Optional[List[Dict[str, Any]]] = None,
    disagreement_threshold: float = 10.0,
) -> EvaluationComparisonSummary:
    """
    Calculate comparison metrics between human evaluation and AI evaluation.

    Formulas:
    - Normalized score = (score / maximum marks) * 100
    - Normalized absolute difference = |human_normalized - ai_normalized|
    - MAE = average of normalized absolute differences across evaluated criteria
    - Agreement percentage = percentage of criteria with normalized difference <= 10 percentage points

    Missing AI scores are handled cleanly without treating missing scores as zero.
    """
    # Ensure inputs are dicts if passed as sqlite3.Row or other Mapping objects
    criteria = [dict(c) if not isinstance(c, dict) else c for c in criteria]
    human_scores = [dict(h) if not isinstance(h, dict) else h for h in human_scores]
    if ai_scores:
        ai_scores = [dict(a) if not isinstance(a, dict) else a for a in ai_scores]

    # Index human scores by criterion_id
    human_map: Dict[int, Dict[str, Any]] = {
        int(item["criterion_id"]): item for item in human_scores
    }

    # Index AI scores by criterion_id if available
    ai_map: Dict[int, Dict[str, Any]] = {}
    if ai_scores:
        for item in ai_scores:
            ai_map[int(item["criterion_id"])] = item

    has_any_ai = len(ai_map) > 0

    criteria_comparisons: List[CriterionComparison] = []
    max_possible_marks = 0.0
    human_total_marks = 0.0
    ai_total_marks = 0.0 if has_any_ai else None

    normalized_differences: List[float] = []
    agreement_count = 0
    comparable_criteria_count = 0

    for crit in criteria:
        c_id = int(crit["id"])
        c_name = crit["name"]
        max_m = float(crit.get("max_score", crit.get("max_marks", 5.0)))
        max_possible_marks += max_m

        # Human score
        h_data = human_map.get(c_id)
        h_score = float(h_data["score"]) if h_data else 0.0
        h_feedback = h_data.get("feedback", "") if h_data else ""
        human_total_marks += h_score
        h_norm = calculate_normalized_score(h_score, max_m)

        # AI score if present
        ai_data = ai_map.get(c_id)
        if ai_data is not None and ai_data.get("score") is not None:
            a_score = float(ai_data["score"])
            if ai_total_marks is not None:
                ai_total_marks += a_score
            a_norm = calculate_normalized_score(a_score, max_m)
            a_reasoning = ai_data.get("reasoning", "")
            a_evidence = ai_data.get("evidence_text", ai_data.get("evidence_excerpt", ""))
            a_location = ai_data.get("evidence_location", "")
            a_uncertainty = ai_data.get("uncertainty", "")

            # Differences
            abs_diff = round(abs(h_score - a_score), 2)
            norm_diff = round(abs(h_norm - a_norm), 2)
            in_agreement = norm_diff <= disagreement_threshold
            significant_disagreement = norm_diff > disagreement_threshold

            normalized_differences.append(norm_diff)
            comparable_criteria_count += 1
            if in_agreement:
                agreement_count += 1

            criteria_comparisons.append(
                CriterionComparison(
                    criterion_id=c_id,
                    criterion_name=c_name,
                    max_marks=max_m,
                    human_score=h_score,
                    human_feedback=h_feedback,
                    ai_score=a_score,
                    ai_reasoning=a_reasoning,
                    ai_evidence_excerpt=a_evidence,
                    ai_evidence_location=a_location,
                    ai_uncertainty=a_uncertainty,
                    human_normalized=h_norm,
                    ai_normalized=a_norm,
                    absolute_difference=abs_diff,
                    normalized_difference=norm_diff,
                    is_in_agreement=in_agreement,
                    significant_disagreement=significant_disagreement,
                )
            )
        else:
            # Human-only or missing AI score for this criterion
            a_reasoning = ai_data.get("reasoning", "") if ai_data else ""
            a_evidence = ai_data.get("evidence_text", ai_data.get("evidence_excerpt", "")) if ai_data else ""
            a_location = ai_data.get("evidence_location", "") if ai_data else ""
            a_uncertainty = ai_data.get("uncertainty", "") if ai_data else ""
            criteria_comparisons.append(
                CriterionComparison(
                    criterion_id=c_id,
                    criterion_name=c_name,
                    max_marks=max_m,
                    human_score=h_score,
                    human_feedback=h_feedback,
                    ai_score=None,
                    ai_reasoning=a_reasoning,
                    ai_evidence_excerpt=a_evidence,
                    ai_evidence_location=a_location,
                    ai_uncertainty=a_uncertainty,
                    human_normalized=h_norm,
                    ai_normalized=None,
                    absolute_difference=None,
                    normalized_difference=None,
                    is_in_agreement=None,
                    significant_disagreement=False,
                )
            )

    # Calculate overall percentages and metrics
    human_percentage = round((human_total_marks / max_possible_marks) * 100.0, 2) if max_possible_marks > 0 else 0.0

    if has_any_ai and ai_total_marks is not None:
        ai_percentage = round((ai_total_marks / max_possible_marks) * 100.0, 2) if max_possible_marks > 0 else 0.0
        total_diff = round(human_total_marks - ai_total_marks, 2)
    else:
        ai_percentage = None
        total_diff = None

    if comparable_criteria_count > 0:
        mae = round(sum(normalized_differences) / comparable_criteria_count, 2)
        agreement_percentage = round((agreement_count / comparable_criteria_count) * 100.0, 2)
    else:
        mae = None
        agreement_percentage = None

    paired_h: List[float] = [c.human_score for c in criteria_comparisons if c.ai_score is not None]
    paired_a: List[float] = [c.ai_score for c in criteria_comparisons if c.ai_score is not None]
    corr = calculate_pearson_correlation(paired_h, paired_a)

    return EvaluationComparisonSummary(
        evaluation_id=evaluation_id,
        evaluation_title=evaluation_title,
        has_ai_evaluation=has_any_ai,
        max_possible_marks=round(max_possible_marks, 2),
        human_total_marks=round(human_total_marks, 2),
        human_percentage=human_percentage,
        ai_total_marks=round(ai_total_marks, 2) if ai_total_marks is not None else None,
        ai_percentage=ai_percentage,
        total_difference=total_diff,
        mae=mae,
        agreement_percentage=agreement_percentage,
        directional_bias=total_diff,
        correlation=corr,
        criteria_comparisons=criteria_comparisons,
    )
