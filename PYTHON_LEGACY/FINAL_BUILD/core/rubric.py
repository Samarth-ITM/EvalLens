"""
Rubric and Criteria Management for EvalLens.

Provides models and operations for creating, editing, adding, removing,
reordering criteria, calculating total marks, and approving rubrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.validators import CriteriaProposalResponse, CriterionProposal
from database.db import save_ai_criteria_proposals, save_approved_rubric


@dataclass
class EditableCriterion:
    """An individual criterion that can be reviewed, edited, or reordered by the human evaluator."""

    name: str
    description: str
    why_it_matters: str = ""
    max_marks: float = 5.0
    weight: float = 1.0
    evidence_guidance: str = ""
    evidence_excerpt: str = ""
    evidence_location: str = ""
    scoring_guidance: str = ""
    is_ai_generated: bool = True
    order_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert criterion to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "why_it_matters": self.why_it_matters,
            "max_marks": self.max_marks,
            "max_score": self.max_marks,
            "weight": self.weight,
            "evidence_guidance": self.evidence_guidance,
            "evidence_excerpt": self.evidence_excerpt,
            "evidence_location": self.evidence_location,
            "scoring_guidance": self.scoring_guidance,
            "is_ai_generated": self.is_ai_generated,
            "order_index": self.order_index,
        }


@dataclass
class EditableRubric:
    """An in-memory rubric containing a collection of editable criteria."""

    title: str
    description: str = ""
    criteria: List[EditableCriterion] = field(default_factory=list)
    prompt_version: str = "V3"
    is_approved: bool = False

    @property
    def total_marks(self) -> float:
        """Calculate the sum of maximum marks across all criteria."""
        return sum(c.max_marks for c in self.criteria)

    def add_criterion(
        self,
        name: str = "New Criterion",
        description: str = "",
        why_it_matters: str = "",
        max_marks: float = 5.0,
        evidence_guidance: str = "",
        scoring_guidance: str = "",
    ) -> EditableCriterion:
        """Add a new custom criterion created by the evaluator."""
        new_crit = EditableCriterion(
            name=name,
            description=description,
            why_it_matters=why_it_matters,
            max_marks=max_marks,
            evidence_guidance=evidence_guidance,
            scoring_guidance=scoring_guidance,
            is_ai_generated=False,
            order_index=len(self.criteria),
        )
        self.criteria.append(new_crit)
        return new_crit

    def remove_criterion(self, index: int) -> None:
        """Remove a criterion at the given index."""
        if 0 <= index < len(self.criteria):
            self.criteria.pop(index)
            # Re-index remaining criteria
            for idx, c in enumerate(self.criteria):
                c.order_index = idx

    def move_up(self, index: int) -> None:
        """Move a criterion up in the order."""
        if index > 0 and index < len(self.criteria):
            self.criteria[index - 1], self.criteria[index] = (
                self.criteria[index],
                self.criteria[index - 1],
            )
            for idx, c in enumerate(self.criteria):
                c.order_index = idx

    def move_down(self, index: int) -> None:
        """Move a criterion down in the order."""
        if 0 <= index < len(self.criteria) - 1:
            self.criteria[index + 1], self.criteria[index] = (
                self.criteria[index],
                self.criteria[index + 1],
            )
            for idx, c in enumerate(self.criteria):
                c.order_index = idx

    @classmethod
    def from_ai_proposal(
        cls,
        proposal: CriteriaProposalResponse,
        title: str,
        description: str = "",
    ) -> EditableRubric:
        """Construct an EditableRubric from an AI CriteriaProposalResponse."""
        editable_criteria: List[EditableCriterion] = []
        for idx, p in enumerate(proposal.criteria):
            editable_criteria.append(
                EditableCriterion(
                    name=p.name,
                    description=p.description,
                    why_it_matters=p.why_it_matters,
                    max_marks=p.max_marks,
                    evidence_guidance=p.evidence_guidance,
                    evidence_excerpt=p.evidence_excerpt,
                    evidence_location=p.evidence_location or "",
                    scoring_guidance=p.scoring_guidance,
                    is_ai_generated=True,
                    order_index=idx,
                )
            )

        return cls(
            title=title,
            description=description,
            criteria=editable_criteria,
            prompt_version=proposal.prompt_version,
            is_approved=False,
        )


def record_ai_proposal(
    evaluation_id: int,
    proposal: CriteriaProposalResponse,
    db_path: Optional[Path] = None,
) -> None:
    """Save the pristine AI proposal into ai_criteria_proposals."""
    raw_dicts = [p.model_dump() for p in proposal.criteria]
    save_ai_criteria_proposals(
        evaluation_id=evaluation_id,
        criteria=raw_dicts,
        prompt_version=proposal.prompt_version,
        db_path=db_path,
    )


def approve_rubric(
    evaluation_id: int,
    rubric: EditableRubric,
    db_path: Optional[Path] = None,
) -> int:
    """
    Explicitly approve and persist the rubric into SQLite.
    Returns the newly created rubric_id.
    """
    if not rubric.criteria:
        raise ValueError("Cannot approve a rubric with zero criteria. Please add at least one criterion.")

    criteria_data = [c.to_dict() for c in rubric.criteria]
    rubric_id = save_approved_rubric(
        evaluation_id=evaluation_id,
        title=rubric.title,
        description=rubric.description,
        criteria=criteria_data,
        total_marks=rubric.total_marks,
        prompt_version=rubric.prompt_version,
        db_path=db_path,
    )
    rubric.is_approved = True
    return rubric_id
