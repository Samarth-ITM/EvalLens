"""
Integration Test: Five-User Prototype Usage Simulation.

Simulates 5 concurrent/sequential users (User 1 through User 5) interacting with
the shared EvalLens prototype workspace:
1. User 1: Creates Evaluation #1 (Written Work) with 3 criteria and saves rubric.
2. User 2: Reviews and edits Evaluation #1 rubric, approves it.
3. User 3: Scores Evaluation #1 as a human evaluator (scores persist, independence intact).
4. User 4: Concurrently creates Evaluation #2 (Code Project), approves rubric, and submits human scores.
5. User 5: Runs AI scoring on Evaluation #1 while User 4 queries Evaluation History.
6. Multi-threaded stress: 5 concurrent threads executing simultaneous reads/writes to test
   SQLite WAL mode and busy timeout (ensuring zero database lock errors).
7. Persistence verification: Ensures all records survive fresh database connections.
"""

from __future__ import annotations

import concurrent.futures
import tempfile
from pathlib import Path
import pytest

from core.comparison import calculate_comparison
from core.document_parser import parse_text_content
from core.evaluator import submit_human_evaluation
from core.rubric import EditableCriterion, EditableRubric, approve_rubric
from core.submission import PreparedSubmission, save_submission_to_db
from database.db import (
    get_ai_scores,
    get_connection,
    get_evaluation,
    get_evaluations_summary,
    get_human_scores,
    get_rubric_with_criteria,
    has_human_scores,
    init_db,
    save_ai_scores,
)


@pytest.fixture
def shared_prototype_db() -> Path:
    """Create a temporary shared database file for the 5-user prototype."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    path = Path(temp_file.name)
    init_db(path)
    yield path
    if path.exists():
        path.unlink()
    # Clean up WAL/SHM files if created
    wal_file = Path(f"{path}-wal")
    shm_file = Path(f"{path}-shm")
    if wal_file.exists():
        wal_file.unlink()
    if shm_file.exists():
        shm_file.unlink()


def test_five_user_sequential_and_concurrent_workflow(shared_prototype_db: Path) -> None:
    """Test full evaluation lifecycle across 5 distinct simulated users."""
    db_path = shared_prototype_db

    # -------------------------------------------------------------
    # 1. USER 1: Creates Evaluation #1 (Essay)
    # -------------------------------------------------------------
    user1_content = "This report assesses renewable energy targets and carbon emission strategies..."
    user1_doc = parse_text_content(user1_content, filename="climate_policy.docx")
    user1_sub = PreparedSubmission(
        title="User 1 - Climate Policy Analysis",
        submission_type="Written Work",
        instructions="Evaluate analytical rigor and clarity.",
        reference_material="Paris Accord 2015",
        prompt_version="V3",
        documents=[user1_doc],
        total_words=user1_doc.word_count,
        combined_submission_text=user1_content,
    )
    eval1_id = save_submission_to_db(user1_sub, db_path=db_path)
    assert eval1_id > 0

    # -------------------------------------------------------------
    # 2. USER 2: Reviews, customizes criteria, and approves Rubric for Eval #1
    # -------------------------------------------------------------
    rubric1 = EditableRubric(
        title="Climate Policy Rubric",
        description="Rubric for evaluating climate report",
        prompt_version="V3",
        criteria=[
            EditableCriterion(
                name="Methodological Rigor",
                description="Use of verified data and modeling.",
                max_marks=10.0,
                evidence_guidance="Inspect data section.",
            ),
            EditableCriterion(
                name="Policy Actionability",
                description="Concrete feasibility of proposed policies.",
                max_marks=10.0,
                evidence_guidance="Inspect conclusion recommendations.",
            ),
        ],
    )
    # User 2 adds a 3rd criterion
    rubric1.add_criterion(
        name="Clarity & Structure",
        description="Document organization, executive summary, and grammar.",
        max_marks=5.0,
    )
    assert rubric1.total_marks == 25.0

    rubric1_id = approve_rubric(eval1_id, rubric1, db_path=db_path)
    assert rubric1_id > 0

    # Verify rubric is approved in DB
    rubric_bundle = get_rubric_with_criteria(eval1_id, db_path=db_path)
    assert rubric_bundle is not None
    assert len(rubric_bundle["criteria"]) == 3
    assert rubric_bundle["rubric"]["is_approved"] == 1

    # -------------------------------------------------------------
    # 3. USER 3: Human Evaluator scores Evaluation #1
    # -------------------------------------------------------------
    criteria1 = rubric_bundle["criteria"]
    human_scores_user3 = [
        {"criterion_id": criteria1[0]["id"], "max_marks": criteria1[0]["max_score"], "score": 8.5, "feedback": "Solid methodology."},
        {"criterion_id": criteria1[1]["id"], "max_marks": criteria1[1]["max_score"], "score": 9.0, "feedback": "Actionable policy."},
        {"criterion_id": criteria1[2]["id"], "max_marks": criteria1[2]["max_score"], "score": 4.5, "feedback": "Clear writing."},
    ]
    submit_human_evaluation(
        evaluation_id=eval1_id,
        scores=human_scores_user3,
        evaluator_name="User 3 (Policy Reviewer)",
        db_path=db_path,
    )
    assert has_human_scores(eval1_id, db_path=db_path) is True
    h_scores = get_human_scores(eval1_id, db_path=db_path)
    assert len(h_scores) == 3
    assert sum(r["score"] for r in h_scores) == 22.0

    # -------------------------------------------------------------
    # 4. USER 4: Concurrently creates Evaluation #2 (Code Project)
    # -------------------------------------------------------------
    user4_content = "import asyncio\nasync def handle_req(): return 200"
    user4_doc = parse_text_content(user4_content, filename="server.py")
    user4_sub = PreparedSubmission(
        title="User 4 - Microservice Server",
        submission_type="Code",
        instructions="Adhere to asyncio conventions.",
        reference_material="",
        prompt_version="V3",
        documents=[user4_doc],
        total_words=user4_doc.word_count,
        combined_submission_text=user4_content,
    )
    eval2_id = save_submission_to_db(user4_sub, db_path=db_path)
    assert eval2_id > eval1_id

    rubric2 = EditableRubric(
        title="Server Code Rubric",
        description="Rubric for server code",
        prompt_version="V3",
        criteria=[
            EditableCriterion(name="Async Correctness", description="No blocking calls.", max_marks=10.0),
            EditableCriterion(name="Code Modularity", description="Clean function bounds.", max_marks=10.0),
        ],
    )
    approve_rubric(eval2_id, rubric2, db_path=db_path)

    rubric2_bundle = get_rubric_with_criteria(eval2_id, db_path=db_path)
    crit2 = rubric2_bundle["criteria"]
    submit_human_evaluation(
        evaluation_id=eval2_id,
        scores=[
            {"criterion_id": crit2[0]["id"], "max_marks": crit2[0]["max_score"], "score": 9.5, "feedback": "Proper coroutines."},
            {"criterion_id": crit2[1]["id"], "max_marks": crit2[1]["max_score"], "score": 8.0, "feedback": "Good modules."},
        ],
        evaluator_name="User 4 (Tech Lead)",
        db_path=db_path,
    )

    # -------------------------------------------------------------
    # 5. USER 5: Performs AI Evaluation Scoring on Eval #1 (with 1 missing evidence criterion)
    # -------------------------------------------------------------
    ai_scores_user5 = [
        {
            "criterion_id": criteria1[0]["id"],
            "score": 9.0,
            "reasoning": "Rigorous data analysis cited from emissions registry.",
            "evidence_text": "Section 3 tables",
            "evidence_location": "Page 4",
        },
        {
            "criterion_id": criteria1[1]["id"],
            "score": 8.5,
            "reasoning": "Feasible timelines provided.",
            "evidence_text": "Recommendations block",
            "evidence_location": "Page 7",
        },
        {
            "criterion_id": criteria1[2]["id"],
            "score": None,  # Missing evidence demonstration
            "reasoning": "Executive summary is absent from submitted excerpt.",
            "evidence_text": "Missing evidence in submission.",
            "uncertainty": "Document lacked intro section.",
        },
    ]
    save_ai_scores(
        evaluation_id=eval1_id,
        ai_scores_data=ai_scores_user5,
        model_name="gemini-3.5-flash-lite",
        db_path=db_path,
    )

    # Verify AI scores in DB
    ai_stored = get_ai_scores(eval1_id, db_path=db_path)
    assert len(ai_stored) == 3
    assert ai_stored[0]["score"] == 9.0
    assert ai_stored[1]["score"] == 8.5
    assert ai_stored[2]["score"] is None  # Accurately stored as NULL, not 0.0!

    # Verify Comparison calculation handles missing score cleanly without corrupting MAE
    comp = calculate_comparison(
        evaluation_id=eval1_id,
        evaluation_title="User 1 - Climate Policy Analysis",
        criteria=[dict(c) for c in criteria1],
        human_scores=[dict(r) for r in h_scores],
        ai_scores=[dict(r) for r in ai_stored],
    )
    assert comp.has_ai_evaluation is True
    # Evaluated criteria:
    # Crit 0: H=8.5/10 (85%), AI=9.0/10 (90%) -> Diff = 5%
    # Crit 1: H=9.0/10 (90%), AI=8.5/10 (85%) -> Diff = 5%
    # Crit 2: AI is None -> OMITTED from MAE!
    # Expected MAE = (5% + 5%) / 2 = 5.0%
    assert comp.mae == pytest.approx(5.0, abs=0.01)
    assert comp.agreement_percentage == 100.0


def test_five_user_concurrent_sqlite_wal_stress(shared_prototype_db: Path) -> None:
    """
    Stress test SQLite WAL mode and busy timeout with 5 concurrent threads
    performing simultaneous inserts and selects.
    """
    db_path = shared_prototype_db

    def user_task(user_idx: int) -> int:
        """Simulate a user creating and reading an evaluation."""
        user_content = f"User {user_idx} submitted content for concurrent validation."
        doc = parse_text_content(user_content, filename=f"user_{user_idx}_test.txt")
        sub = PreparedSubmission(
            title=f"Concurrent Test Eval #{user_idx}",
            submission_type="Custom",
            instructions=f"Instructions from user {user_idx}",
            reference_material="",
            prompt_version="V3",
            documents=[doc],
            total_words=doc.word_count,
            combined_submission_text=user_content,
        )
        eval_id = save_submission_to_db(sub, db_path=db_path)

        # Read back
        ev = get_evaluation(eval_id, db_path=db_path)
        assert ev is not None
        assert ev["title"] == f"Concurrent Test Eval #{user_idx}"

        # Summary check
        summary = get_evaluations_summary(db_path=db_path)
        assert len(summary) >= 1
        return eval_id

    # Run 5 concurrent threads representing the 5 testers
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(user_task, i) for i in range(1, 6)]
        results = [f.result(timeout=10.0) for f in futures]

    assert len(results) == 5
    assert len(set(results)) == 5  # 5 unique evaluation IDs created without any locking error!

    # Final count check
    all_evals = get_evaluations_summary(db_path=db_path)
    assert len(all_evals) == 5
