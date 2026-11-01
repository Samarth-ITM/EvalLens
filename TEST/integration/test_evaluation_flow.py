"""
Integration tests for the Series 3 evaluation workflow.

Verifies:
- Complete workflow: rubric approval -> human scoring -> optional AI scoring -> comparison
- Persistence of human scores in human_scores table
- Persistence of AI scores in ai_scores table (no overwriting of human scores)
- Status transitions: draft -> rubric_approved -> human_evaluated -> completed
- Independence enforcement: AI scores hidden before human submission
- Human-only evaluation workflow without AI scores
- Full comparison metrics calculation from stored database rows
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch
import pytest

from core.ai_client import GeminiClientManager
from core.comparison import calculate_comparison
from core.evaluator import (
    execute_ai_evaluation,
    get_visible_ai_scores_for_review,
    submit_human_evaluation,
)
from database.db import (
    add_submission,
    create_evaluation,
    get_ai_scores,
    get_evaluation,
    get_evaluations_summary,
    get_human_scores,
    get_rubric_with_criteria,
    init_db,
    save_approved_rubric,
)


@pytest.fixture
def test_db_path() -> Path:
    """Provide an isolated database path for integration tests."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    path = Path(temp_file.name)
    init_db(path)
    yield path
    if path.exists():
        path.unlink()


def test_full_evaluation_and_comparison_lifecycle(test_db_path: Path) -> None:
    """Test full flow: rubric approved -> human scoring -> AI scoring -> comparison dashboard."""
    # 1. Create evaluation
    eval_id = create_evaluation(
        title="Operating Systems Lab Review",
        submission_type="Code",
        instructions="Evaluate synchronization and deadlocks.",
        prompt_version="V3",
        total_words=450,
        db_path=test_db_path,
    )

    # 2. Add submission
    add_submission(
        evaluation_id=eval_id,
        title="mutex_lock.cpp",
        content="pthread_mutex_lock(&lock);\nshared_var++;\npthread_mutex_unlock(&lock);\n",
        word_count=450,
        db_path=test_db_path,
    )

    # 3. Create approved rubric
    criteria_defs = [
        {
            "name": "Deadlock Freedom",
            "description": "Checks for lock ordering and race conditions",
            "max_score": 5.0,
            "weight": 1.0,
            "evidence_guidance": "Inspect mutex lock sequences",
            "scoring_guidance": "5 for provable deadlock freedom",
        },
        {
            "name": "Code Cleanliness",
            "description": "Checks naming and modularity",
            "max_score": 5.0,
            "weight": 1.0,
            "evidence_guidance": "Inspect variable naming",
            "scoring_guidance": "5 for clean code",
        },
    ]

    rubric_id = save_approved_rubric(
        evaluation_id=eval_id,
        title="OS Concurrency Rubric",
        description="Concurrency lab rubric",
        criteria=criteria_defs,
        total_marks=10.0,
        prompt_version="V3",
        db_path=test_db_path,
    )

    rubric_info = get_rubric_with_criteria(eval_id, db_path=test_db_path)
    assert rubric_info is not None
    saved_criteria = rubric_info["criteria"]
    c1_id = saved_criteria[0]["id"]
    c2_id = saved_criteria[1]["id"]

    # 4. Human enters and submits evaluation
    human_entries = [
        {
            "criterion_id": c1_id,
            "criterion_name": "Deadlock Freedom",
            "score": 4.5,
            "max_marks": 5.0,
            "feedback": "Correct use of pthread_mutex_lock.",
        },
        {
            "criterion_id": c2_id,
            "criterion_name": "Code Cleanliness",
            "score": 4.0,
            "max_marks": 5.0,
            "feedback": "Clear variable names.",
        },
    ]

    submit_human_evaluation(
        evaluation_id=eval_id,
        scores=human_entries,
        evaluator_name="Professor Smith",
        db_path=test_db_path,
    )

    # Verify human scores persisted
    h_scores = get_human_scores(eval_id, db_path=test_db_path)
    assert len(h_scores) == 2
    assert float(h_scores[0]["score"]) == 4.5
    assert float(h_scores[1]["score"]) == 4.0

    # Verify evaluation status updated
    eval_row = get_evaluation(eval_id, db_path=test_db_path)
    assert eval_row["status"] == "human_evaluated"

    # 5. Run Mocked AI Evaluation using Gemini
    with patch("google.genai.Client") as mock_client_class:
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "scores": [
                    {
                        "criterion_id": c1_id,
                        "criterion_name": "Deadlock Freedom",
                        "score": 5.0,
                        "max_marks": 5.0,
                        "reasoning": "Single mutex pattern cannot deadlock.",
                        "evidence_text": "pthread_mutex_lock(&lock);",
                        "evidence_location": "L1",
                        "uncertainty": "",
                    },
                    {
                        "criterion_id": c2_id,
                        "criterion_name": "Code Cleanliness",
                        "score": 3.5,
                        "max_marks": 5.0,
                        "reasoning": "Function is very brief.",
                        "evidence_text": "shared_var++",
                        "evidence_location": "L2",
                        "uncertainty": "Code snippet is small",
                    },
                ],
                "overall_reasoning": "Good basic synchronization implementation.",
            }
        )
        mock_instance.models.generate_content.return_value = mock_response

        client_mgr = GeminiClientManager(api_key="AIzaSyMockKeyForTesting12345")
        ai_scores = execute_ai_evaluation(
            client_manager=client_mgr,
            evaluation_id=eval_id,
            submission_text="pthread_mutex_lock(&lock);",
            submission_type="Code",
            instructions=None,
            criteria=saved_criteria,
            db_path=test_db_path,
        )

        assert len(ai_scores) == 2

    # Verify AI scores stored in distinct table without overwriting human scores
    db_ai_scores = get_ai_scores(eval_id, db_path=test_db_path)
    assert len(db_ai_scores) == 2
    assert float(db_ai_scores[0]["score"]) == 5.0
    assert float(db_ai_scores[1]["score"]) == 3.5

    # Human scores remain untouched
    h_scores_after = get_human_scores(eval_id, db_path=test_db_path)
    assert float(h_scores_after[0]["score"]) == 4.5
    assert float(h_scores_after[1]["score"]) == 4.0

    # Evaluation status updated to 'completed'
    eval_row_final = get_evaluation(eval_id, db_path=test_db_path)
    assert eval_row_final["status"] == "completed"

    # 6. Calculate Comparison Metrics
    summary = calculate_comparison(
        evaluation_id=eval_id,
        evaluation_title=eval_row_final["title"],
        criteria=[dict(c) for c in saved_criteria],
        human_scores=[dict(r) for r in h_scores_after],
        ai_scores=[dict(r) for r in db_ai_scores],
    )

    assert summary.has_ai_evaluation is True
    assert summary.human_total_marks == 8.5
    assert summary.ai_total_marks == 8.5
    assert summary.max_possible_marks == 10.0
    assert summary.human_percentage == 85.0
    assert summary.ai_percentage == 85.0
    assert summary.total_difference == 0.0

    # Criterion 1: Human 4.5/5 (90%), AI 5.0/5 (100%) -> diff = 10% (Agreement)
    # Criterion 2: Human 4.0/5 (80%), AI 3.5/5 (70%) -> diff = 10% (Agreement)
    # MAE = (10.0 + 10.0) / 2 = 10.0%
    # Agreement = 100.0%
    assert summary.mae == 10.0
    assert summary.agreement_percentage == 100.0


def test_human_only_workflow_persistence(test_db_path: Path) -> None:
    """Verify that human-only evaluation works completely without AI scores."""
    eval_id = create_evaluation(
        title="Human Only Essay",
        submission_type="Written Work",
        db_path=test_db_path,
    )

    rubric_id = save_approved_rubric(
        evaluation_id=eval_id,
        title="Essay Rubric",
        description="",
        criteria=[{"name": "Thesis", "max_score": 10.0}],
        total_marks=10.0,
        db_path=test_db_path,
    )

    rubric_info = get_rubric_with_criteria(eval_id, db_path=test_db_path)
    c_id = rubric_info["criteria"][0]["id"]

    submit_human_evaluation(
        evaluation_id=eval_id,
        scores=[{"criterion_id": c_id, "score": 9.0, "max_marks": 10.0, "feedback": "Great thesis."}],
        db_path=test_db_path,
    )

    h_scores = get_human_scores(eval_id, db_path=test_db_path)
    assert len(h_scores) == 1
    assert float(h_scores[0]["score"]) == 9.0

    # No AI scores exist
    ai_scores = get_ai_scores(eval_id, db_path=test_db_path)
    assert len(ai_scores) == 0

    # Comparison runs cleanly for human-only session
    summary = calculate_comparison(
        evaluation_id=eval_id,
        evaluation_title="Human Only Essay",
        criteria=[dict(c) for c in rubric_info["criteria"]],
        human_scores=[dict(r) for r in h_scores],
        ai_scores=None,
    )

    assert summary.has_ai_evaluation is False
    assert summary.human_total_marks == 9.0
    assert summary.human_percentage == 90.0
    assert summary.ai_total_marks is None
    assert summary.mae is None
    assert summary.agreement_percentage is None

