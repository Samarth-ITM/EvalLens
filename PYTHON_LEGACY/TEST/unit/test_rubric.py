"""
Unit tests for core/rubric.py.

Verifies:
- Rubric construction from AI proposal
- Dynamic calculation of total marks
- Adding, editing, and deleting criteria
- Reordering criteria (move up, move down)
- Preserving AI vs human creation flags
"""

from __future__ import annotations

from core.rubric import EditableCriterion, EditableRubric
from core.validators import CriteriaProposalResponse, CriterionProposal


def test_rubric_creation_and_total_marks() -> None:
    """Verify total marks calculates correctly across criteria."""
    proposal = CriteriaProposalResponse(
        criteria=[
            CriterionProposal(
                name="Correctness",
                description="Checks functional accuracy",
                max_marks=5.0,
            ),
            CriterionProposal(
                name="Clarity",
                description="Checks writing clarity",
                max_marks=3.0,
            ),
            CriterionProposal(
                name="Structure",
                description="Checks organization",
                max_marks=2.0,
            ),
        ],
        prompt_version="V3",
    )

    rubric = EditableRubric.from_ai_proposal(proposal, title="Essay Rubric")
    assert len(rubric.criteria) == 3
    assert rubric.total_marks == 10.0
    assert rubric.criteria[0].is_ai_generated is True


def test_rubric_editing_and_reordering() -> None:
    """Verify adding, editing, moving, and removing criteria."""
    rubric = EditableRubric(title="Test Rubric")
    crit1 = rubric.add_criterion("Criteria A", "First", max_marks=4.0)
    crit2 = rubric.add_criterion("Criteria B", "Second", max_marks=6.0)

    assert len(rubric.criteria) == 2
    assert rubric.total_marks == 10.0
    assert rubric.criteria[0].name == "Criteria A"

    # Move down
    rubric.move_down(0)
    assert rubric.criteria[0].name == "Criteria B"
    assert rubric.criteria[1].name == "Criteria A"

    # Move up
    rubric.move_up(1)
    assert rubric.criteria[0].name == "Criteria A"
    assert rubric.criteria[1].name == "Criteria B"

    # Edit max marks
    rubric.criteria[0].max_marks = 8.0
    assert rubric.total_marks == 14.0

    # Delete
    rubric.remove_criterion(0)
    assert len(rubric.criteria) == 1
    assert rubric.criteria[0].name == "Criteria B"
    assert rubric.total_marks == 6.0

