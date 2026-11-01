"""
Integration tests for submission workflow and rubric database persistence.

Verifies:
- Combining text and file uploads in prepare_submission
- Saving submission metadata and content to SQLite
- Persisting pristine AI proposals in ai_criteria_proposals
- Persisting human-approved rubrics and criteria in rubrics / rubric_criteria
- Keeping AI proposal and approved rubric distinguishable
- Updating evaluation status to 'rubric_approved'
"""

from __future__ import annotations

import tempfile
from pathlib import Path
import pytest

from core.rubric import EditableCriterion, EditableRubric, approve_rubric, record_ai_proposal
from core.submission import prepare_submission, save_submission_to_db
from core.validators import CriteriaProposalResponse, CriterionProposal
from database.db import (
    get_ai_criteria_proposals,
    get_evaluation,
    get_evaluations_summary,
    get_rubric_with_criteria,
    get_submissions_for_evaluation,
    init_db,
)


@pytest.fixture
def test_db_path() -> Path:
    """Provide a temporary database path for integration tests."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    path = Path(temp_file.name)
    init_db(path)
    yield path
    if path.exists():
        path.unlink()


def test_submission_and_rubric_persistence_lifecycle(test_db_path: Path) -> None:
    """Test the complete submission -> AI proposal -> rubric approval -> DB persistence flow."""
    # 1. Prepare submission with text and a sample code file
    pasted = "def add(x, y):\n    return x + y\n"
    uploaded_files = [
        ("utils.py", b"def multiply(a, b):\n    return a * b\n"),
        ("notes.txt", b"Helper notes for arithmetic module.\n"),
    ]

    prepared = prepare_submission(
        title="Math Module Review",
        submission_type="Code",
        instructions="Ensure functions have type hints and docstrings.",
        reference_material="Coding Standards 2026",
        pasted_text=pasted,
        uploaded_files=uploaded_files,
        prompt_version="V3",
    )

    assert prepared.total_words > 0
    assert len(prepared.documents) == 3

    # 2. Save submission to database
    eval_id = save_submission_to_db(
        prepared, uploaded_files_data=uploaded_files, db_path=test_db_path
    )
    assert eval_id > 0

    # Verify evaluation row
    eval_row = get_evaluation(eval_id, db_path=test_db_path)
    assert eval_row is not None
    assert eval_row["title"] == "Math Module Review"
    assert eval_row["submission_type"] == "Code"
    assert eval_row["total_words"] == prepared.total_words

    # Verify submission rows
    subs = get_submissions_for_evaluation(eval_id, db_path=test_db_path)
    assert len(subs) == 3


def test_db_rubric_approval_isolation(test_db_path: Path) -> None:
    """Test storing AI proposals and approved rubrics distinctly in the test database."""
    from database.db import create_evaluation, add_submission

    # 1. Create evaluation
    eval_id = create_evaluation(
        title="Architecture Review",
        submission_type="Technical Report",
        instructions="Review modularity.",
        prompt_version="V3",
        total_words=250,
        db_path=test_db_path,
    )

    # 2. Add submission record
    sub_id = add_submission(
        evaluation_id=eval_id,
        title="report.md",
        content="System Architecture Report content...",
        file_name="report.md",
        word_count=250,
        db_path=test_db_path,
    )
    assert sub_id > 0

    # 3. Record pristine AI proposal
    ai_proposal = CriteriaProposalResponse(
        criteria=[
            CriterionProposal(
                name="AI Modularity",
                description="Checks modular separation",
                why_it_matters="Scalability",
                max_marks=5.0,
                evidence_guidance="Inspect component boundaries",
                evidence_excerpt="System Architecture Report",
                evidence_location="L1-L10",
                scoring_guidance="Award 5 for high cohesion",
            ),
            CriterionProposal(
                name="AI Fault Tolerance",
                description="Checks resilience",
                why_it_matters="Reliability",
                max_marks=5.0,
                evidence_guidance="Inspect circuit breakers",
                evidence_excerpt="Component boundaries",
                evidence_location="L12",
                scoring_guidance="Award 5 for fallback handlers",
            ),
        ],
        prompt_version="V3",
    )
    record_ai_proposal(evaluation_id=eval_id, proposal=ai_proposal, db_path=test_db_path)

    # Verify AI proposals saved
    proposals = get_ai_criteria_proposals(evaluation_id=eval_id, db_path=test_db_path)
    assert len(proposals) == 2
    assert proposals[0]["name"] == "AI Modularity"

    # 4. Human modifies and adds a criterion, then approves rubric
    editable_rubric = EditableRubric.from_ai_proposal(ai_proposal, title="Approved System Rubric")
    # Human edits first criterion
    editable_rubric.criteria[0].name = "Human-Approved Modularity"
    editable_rubric.criteria[0].max_marks = 8.0
    # Human adds custom criterion
    editable_rubric.add_criterion(
        name="Security Architecture",
        description="Evaluates threat model and secret storage",
        max_marks=7.0,
    )

    assert editable_rubric.total_marks == 20.0  # 8.0 + 5.0 + 7.0

    rubric_id = approve_rubric(
        evaluation_id=eval_id, rubric=editable_rubric, db_path=test_db_path
    )
    assert rubric_id > 0

    # 5. Verify the AI proposals and the approved rubric are distinct in DB
    stored_proposals = get_ai_criteria_proposals(evaluation_id=eval_id, db_path=test_db_path)
    assert len(stored_proposals) == 2
    assert stored_proposals[0]["name"] == "AI Modularity"  # Pristine AI proposal remains unchanged!

    approved_data = get_rubric_with_criteria(evaluation_id=eval_id, db_path=test_db_path)
    assert approved_data is not None
    assert approved_data["rubric"]["status"] == "approved"
    assert approved_data["rubric"]["total_marks"] == 20.0
    assert len(approved_data["criteria"]) == 3
    assert approved_data["criteria"][0]["name"] == "Human-Approved Modularity"
    assert approved_data["criteria"][0]["max_score"] == 8.0
    assert approved_data["criteria"][2]["name"] == "Security Architecture"
    assert approved_data["criteria"][2]["is_ai_generated"] == 0

    # 6. Verify evaluation status updated to 'rubric_approved'
    eval_row = get_evaluation(evaluation_id=eval_id, db_path=test_db_path)
    assert eval_row["status"] == "rubric_approved"

    # 7. Verify summary includes approved total marks
    summaries = get_evaluations_summary(db_path=test_db_path)
    assert len(summaries) >= 1
    target_summary = next(s for s in summaries if s["id"] == eval_id)
    assert target_summary["approved_total_marks"] == 20.0
    assert target_summary["status"] == "rubric_approved"
