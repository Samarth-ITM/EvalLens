"""
Integration tests for approved rubric integrity and historical score protection.

Verifies:
- An approved rubric cannot be silently modified or overwritten once human scoring starts.
- An approved rubric cannot be silently modified or overwritten once AI scoring starts.
- Attempting to overwrite an approved rubric after scoring has begun raises ValueError.
- Historical evaluations, rubrics, and scores remain fully readable and intact.
- Separate evaluations can evaluate with different or modified rubrics without affecting existing evaluations.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from database.db import (
    create_evaluation,
    get_evaluation,
    get_human_scores,
    get_ai_scores,
    get_rubric_with_criteria,
    init_db,
    save_approved_rubric,
    save_human_scores,
    save_ai_scores,
)
from core.rubric import EditableCriterion, EditableRubric, approve_rubric


def test_rubric_cannot_be_modified_after_human_scoring_begins(tmp_path: Path) -> None:
    """
    CRITICAL RUBRIC INTEGRITY RULE:
    Once human scoring has commenced, calling save_approved_rubric or approve_rubric
    for that evaluation MUST raise ValueError.
    """
    db_file = tmp_path / "rubric_integrity_human.db"
    init_db(db_file)

    # 1. Create evaluation
    eval_id = create_evaluation(
        title="Research Paper Evaluation",
        submission_type="Written Work",
        db_path=db_file,
    )

    # 2. Approve initial rubric
    initial_criteria = [
        {"name": "Methodology", "max_score": 5.0, "description": "Original methodology"},
        {"name": "Results", "max_score": 5.0, "description": "Original results"},
    ]
    rubric_id = save_approved_rubric(
        evaluation_id=eval_id,
        title="Initial Research Rubric",
        description="Version 1",
        criteria=initial_criteria,
        total_marks=10.0,
        db_path=db_file,
    )

    rubric_data = get_rubric_with_criteria(eval_id, db_path=db_file)
    assert rubric_data is not None
    crit1_id = rubric_data["criteria"][0]["id"]
    crit2_id = rubric_data["criteria"][1]["id"]

    # 3. Human evaluator submits scores
    save_human_scores(
        evaluation_id=eval_id,
        scores_data=[
            {"criterion_id": crit1_id, "score": 4.5, "feedback": "Solid method"},
            {"criterion_id": crit2_id, "score": 4.0, "feedback": "Good results"},
        ],
        evaluator_name="Prof. Smith",
        db_path=db_file,
    )

    # 4. Attempt to modify or re-approve rubric for this evaluation
    modified_criteria = [
        {"name": "Methodology", "max_score": 10.0, "description": "Changed max score"},
        {"name": "Writing Style", "max_score": 5.0, "description": "Replaced results"},
    ]

    with pytest.raises(ValueError) as excinfo:
        save_approved_rubric(
            evaluation_id=eval_id,
            title="Modified Rubric",
            description="Trying to mutate existing rubric",
            criteria=modified_criteria,
            total_marks=15.0,
            db_path=db_file,
        )
    assert "Cannot modify approved rubric" in str(excinfo.value)
    assert "scoring has already commenced" in str(excinfo.value)

    # 5. Verify original rubric and human scores remain completely intact
    persisted = get_rubric_with_criteria(eval_id, db_path=db_file)
    assert persisted is not None
    assert persisted["rubric"]["title"] == "Initial Research Rubric"
    assert len(persisted["criteria"]) == 2
    assert persisted["criteria"][0]["name"] == "Methodology"
    assert persisted["criteria"][0]["max_score"] == 5.0

    scores = get_human_scores(eval_id, db_path=db_file)
    assert len(scores) == 2
    assert scores[0]["score"] == 4.5
    assert scores[0]["feedback"] == "Solid method"


def test_rubric_cannot_be_modified_after_ai_scoring_begins(tmp_path: Path) -> None:
    """
    Verify that if AI scores exist, rubric cannot be modified either.
    """
    db_file = tmp_path / "rubric_integrity_ai.db"
    init_db(db_file)

    eval_id = create_evaluation(
        title="Code Review Session",
        submission_type="Code",
        db_path=db_file,
    )

    rubric_id = save_approved_rubric(
        evaluation_id=eval_id,
        title="Code Review Rubric",
        description="Initial version",
        criteria=[{"name": "Code Security", "max_score": 5.0}],
        total_marks=5.0,
        db_path=db_file,
    )

    rubric_data = get_rubric_with_criteria(eval_id, db_path=db_file)
    assert rubric_data is not None
    crit_id = rubric_data["criteria"][0]["id"]

    # AI saves scores
    save_ai_scores(
        evaluation_id=eval_id,
        ai_scores_data=[
            {
                "criterion_id": crit_id,
                "score": 4.5,
                "reasoning": "Secure coding practices observed",
                "evidence_text": "def sanitize()",
            }
        ],
        model_name="gemini-3.8-flash",
        db_path=db_file,
    )

    # Attempt to overwrite rubric
    with pytest.raises(ValueError, match="Cannot modify approved rubric"):
        save_approved_rubric(
            evaluation_id=eval_id,
            title="Altered Rubric",
            description="Mutation attempt",
            criteria=[{"name": "Altered Criterion", "max_score": 20.0}],
            total_marks=20.0,
            db_path=db_file,
        )

    # Verify AI score remains associated
    ai_scores = get_ai_scores(eval_id, db_path=db_file)
    assert len(ai_scores) == 1
    assert ai_scores[0]["score"] == 4.5


def test_new_evaluation_allows_modified_rubric_without_touching_historical(tmp_path: Path) -> None:
    """
    Verify that creating a new evaluation permits evaluating with a modified rubric
    while keeping the historical evaluation completely unaltered.
    """
    db_file = tmp_path / "multi_eval_rubric.db"
    init_db(db_file)

    # Eval 1: Historical
    eval1_id = create_evaluation(title="Historical Eval 1", submission_type="Custom", db_path=db_file)
    save_approved_rubric(
        evaluation_id=eval1_id,
        title="Rubric V1",
        description="Version 1",
        criteria=[{"name": "Criterion 1", "max_score": 5.0}],
        total_marks=5.0,
        db_path=db_file,
    )
    r1_data = get_rubric_with_criteria(eval1_id, db_path=db_file)
    save_human_scores(
        eval1_id,
        [{"criterion_id": r1_data["criteria"][0]["id"], "score": 4.0}],
        db_path=db_file,
    )

    # Eval 2: New Evaluation with different/updated rubric
    eval2_id = create_evaluation(title="Follow-up Eval 2", submission_type="Custom", db_path=db_file)
    save_approved_rubric(
        evaluation_id=eval2_id,
        title="Rubric V2 (Updated)",
        description="Updated criteria",
        criteria=[
            {"name": "Criterion 1", "max_score": 10.0},
            {"name": "Criterion 2", "max_score": 10.0},
        ],
        total_marks=20.0,
        db_path=db_file,
    )

    # Verify Eval 1 is untouched
    e1_rubric = get_rubric_with_criteria(eval1_id, db_path=db_file)
    assert e1_rubric["rubric"]["total_marks"] == 5.0
    assert len(e1_rubric["criteria"]) == 1

    # Verify Eval 2 has the updated rubric
    e2_rubric = get_rubric_with_criteria(eval2_id, db_path=db_file)
    assert e2_rubric["rubric"]["total_marks"] == 20.0
    assert len(e2_rubric["criteria"]) == 2

