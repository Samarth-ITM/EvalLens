"""
Evaluation Orchestration for EvalLens.

Coordinates:
- Human score validation and persistence
- Independent AI rubric scoring using the exact approved criteria
- Strict score validation (clamped to [0, max_marks])
- Enforcement of the Independence Rule (AI scores hidden until human submission is complete)
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.ai_client import GeminiClientManager, sanitize_error_message
from core.criteria_generator import clean_json_text
from core.validators import AICriterionScoreResult, AIEvaluationResponse, HumanCriterionScoreInput
from database.db import (
    get_ai_scores,
    get_human_scores,
    has_human_scores,
    save_ai_scores,
    save_human_scores,
)

logger = logging.getLogger(__name__)


def validate_human_score(score: float, max_marks: float, criterion_name: str = "") -> float:
    """
    Validate that a human-entered score is non-negative and does not exceed maximum marks.
    """
    if score < 0.0:
        raise ValueError(
            f"Score for '{criterion_name or 'criterion'}' cannot be negative (got {score})."
        )
    if score > max_marks:
        raise ValueError(
            f"Score for '{criterion_name or 'criterion'}' ({score}) cannot exceed the maximum of {max_marks} marks."
        )
    return round(score, 2)


def submit_human_evaluation(
    evaluation_id: int,
    scores: List[Dict[str, Any]],
    evaluator_name: str = "Human Evaluator",
    db_path: Optional[Path] = None,
) -> None:
    """
    Validate and persist human evaluation scores to SQLite.
    Does NOT touch AI scores.
    """
    validated_scores: List[Dict[str, Any]] = []
    for item in scores:
        c_id = int(item["criterion_id"])
        c_name = item.get("criterion_name", f"Criterion #{c_id}")
        raw_score = float(item["score"])
        max_marks = float(item["max_marks"])

        val_score = validate_human_score(raw_score, max_marks, c_name)
        validated_scores.append(
            {
                "criterion_id": c_id,
                "score": val_score,
                "feedback": item.get("feedback", "").strip(),
            }
        )

    save_human_scores(
        evaluation_id=evaluation_id,
        scores_data=validated_scores,
        evaluator_name=evaluator_name,
        db_path=db_path,
    )


def build_ai_scoring_prompt(
    submission_text: str,
    submission_type: str,
    instructions: Optional[str],
    criteria: List[Dict[str, Any]],
) -> str:
    """
    Construct the prompt requiring Gemini to score the submission using ONLY
    the exact human-approved criteria without creating or altering criteria.
    """
    criteria_blocks: List[str] = []
    for idx, c in enumerate(criteria):
        c_id = c["id"]
        c_name = c["name"]
        max_m = float(c.get("max_score", c.get("max_marks", 5.0)))
        desc = c.get("description", "")
        guidance = c.get("evidence_guidance", "")
        scoring = c.get("scoring_guidance", "")

        criteria_blocks.append(
            f"Criterion ID: {c_id}\n"
            f"Name: {c_name}\n"
            f"Description: {desc}\n"
            f"Maximum Marks: {max_m}\n"
            f"Evidence Guidance: {guidance}\n"
            f"Scoring Guidance: {scoring}\n"
        )

    criteria_str = "\n---\n".join(criteria_blocks)
    instructions_block = (
        f"Evaluator Instructions:\n{instructions}\n" if instructions else ""
    )

    return f"""You are an objective, independent AI evaluation assistant for EvalLens.
Your task is to evaluate the submitted work using EXCLUSIVELY the approved evaluation criteria listed below.

CRITICAL INSTRUCTIONS:
1. You MUST evaluate every single criterion listed below. Do NOT add new criteria or modify existing criteria.
2. For each criterion, award a score between 0.0 and the criterion's Maximum Marks.
3. Scores MUST NOT exceed the specified Maximum Marks.
4. Provide a clear, objective explanation ('reasoning') justifying the score.
5. In 'evidence_text', cite verbatim supporting text from the submission. If evidence is missing, state this clearly and reflect it in the score.
6. In 'evidence_location', cite the page or line number only if present in the text (e.g. 'L14', 'Page 2').
7. In 'uncertainty', note any limitations, ambiguities, or missing information.
8. NEVER invent or hallucinate evidence or quotations.

Submission Type: {submission_type}
{instructions_block}

Submission Content:
\"\"\"
{submission_text}
\"\"\"

Approved Evaluation Criteria:
{criteria_str}

Respond ONLY with a valid JSON object matching this schema:
{{
  "scores": [
    {{
      "criterion_id": 1,
      "criterion_name": "Criterion Name",
      "score": 4.5,
      "max_marks": 5.0,
      "reasoning": "Detailed justification...",
      "evidence_text": "Verbatim excerpt...",
      "evidence_location": "L12-L15",
      "uncertainty": "Note any missing info or leave empty"
    }}
  ],
  "overall_reasoning": "Summary of AI evaluation..."
}}
"""


def parse_and_validate_ai_response(
    raw_response_text: str,
    criteria: List[Dict[str, Any]],
    model_name: str,
) -> List[Dict[str, Any]]:
    """
    Parse Gemini response, validate with Pydantic, and ensure scores do not exceed criteria maximums.
    """
    clean_json = clean_json_text(raw_response_text)
    try:
        data = json.loads(clean_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned an invalid JSON response: {e}")

    if not isinstance(data, dict) or "scores" not in data:
        raise ValueError("Malformed AI response: 'scores' list is missing.")

    data["model_name"] = model_name
    validated_response = AIEvaluationResponse.model_validate(data)

    # Build lookup map of approved criteria
    criteria_map: Dict[int, Dict[str, Any]] = {int(c["id"]): c for c in criteria}

    sanitized_scores: List[Dict[str, Any]] = []
    for s in validated_response.scores:
        c_id = s.criterion_id
        if c_id not in criteria_map:
            logger.warning(f"AI returned score for unknown criterion ID {c_id}; skipping.")
            continue

        c_meta = criteria_map[c_id]
        max_allowed = float(c_meta.get("max_score", c_meta.get("max_marks", 5.0)))

        # Validate score bounds
        final_score = s.score
        if final_score < 0.0:
            final_score = 0.0
        elif final_score > max_allowed:
            logger.warning(
                f"AI score ({final_score}) exceeded max marks ({max_allowed}) for {s.criterion_name}. Clamping to max."
            )
            final_score = max_allowed

        sanitized_scores.append(
            {
                "criterion_id": c_id,
                "criterion_name": s.criterion_name,
                "score": round(final_score, 2),
                "max_marks": max_allowed,
                "reasoning": s.reasoning,
                "evidence_text": s.evidence_text or "",
                "evidence_location": s.evidence_location or "",
                "uncertainty": s.uncertainty or "",
            }
        )

    if not sanitized_scores:
        raise ValueError("No valid criterion scores could be parsed from the AI response.")

    return sanitized_scores


def execute_ai_evaluation(
    client_manager: GeminiClientManager,
    evaluation_id: int,
    submission_text: str,
    submission_type: str,
    instructions: Optional[str],
    criteria: List[Dict[str, Any]],
    db_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Execute AI evaluation against the approved rubric using Gemini and persist scores to SQLite.
    Never overwrites human scores.
    """
    if not client_manager.has_key:
        raise ValueError("Add your Gemini API key in Settings to run AI evaluation.")

    prompt = build_ai_scoring_prompt(
        submission_text=submission_text,
        submission_type=submission_type,
        instructions=instructions,
        criteria=criteria,
    )

    try:
        from google import genai

        client = genai.Client(api_key=client_manager._api_key)
        response = client.models.generate_content(
            model=client_manager.model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.1,
            },
        )

        response_text = getattr(response, "text", "") or ""
        if not response_text:
            raise ValueError("Gemini returned an empty response.")

        ai_scores = parse_and_validate_ai_response(
            raw_response_text=response_text,
            criteria=criteria,
            model_name=client_manager.model_name,
        )

        # Persist scores in separate ai_scores table
        save_ai_scores(
            evaluation_id=evaluation_id,
            ai_scores_data=ai_scores,
            model_name=client_manager.model_name,
            db_path=db_path,
        )

        return ai_scores

    except Exception as e:
        safe_msg = sanitize_error_message(e, client_manager._api_key)
        raise RuntimeError(safe_msg)


def get_visible_ai_scores_for_review(
    evaluation_id: int, db_path: Optional[Path] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Enforces the Independence Rule:
    AI scores must remain strictly hidden until the human evaluation is submitted.
    If human evaluation is not yet submitted, returns None.
    """
    if not has_human_scores(evaluation_id, db_path=db_path):
        return None

    raw_scores = get_ai_scores(evaluation_id, db_path=db_path)
    return [dict(row) for row in raw_scores] if raw_scores else None
