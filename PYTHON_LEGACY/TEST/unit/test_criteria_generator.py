"""
Unit tests for core/criteria_generator.py.

Verifies:
- Prompt versions V1, V2, and V3 generation
- JSON parsing and markdown fence stripping
- Pydantic schema validation for criteria proposals
- Deduplication of criteria names
- Handling invalid JSON from AI
- Safe handling of missing Gemini key
- Safe exception sanitization on API failures
- Mocked Gemini criteria generation
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
import pytest
from pydantic import ValidationError

from core.ai_client import GeminiClientManager
from core.criteria_generator import (
    DEFAULT_PROMPT_VERSION,
    build_prompt_by_version,
    build_prompt_v1,
    build_prompt_v2,
    build_prompt_v3,
    clean_json_text,
    generate_criteria,
)
from core.validators import CriteriaProposalResponse, CriterionProposal


def test_prompt_versions_building() -> None:
    """Verify that V1, V2, and V3 prompts are constructed with appropriate sections."""
    sub_text = "def calculate_tax(income): return income * 0.2"

    v1 = build_prompt_v1(sub_text, "Code")
    assert "Submission Type: Code" in v1
    assert sub_text in v1
    assert "limitation_note" in v1

    v2 = build_prompt_v2(sub_text, "Code", instructions="Focus on PEP8", reference_material="Tax law 2026")
    assert "Focus on PEP8" in v2
    assert "Tax law 2026" in v2

    v3 = build_prompt_v3(sub_text, "Code", instructions="Check error handling", reference_material="Rubric Guide")
    assert "CRITICAL EVIDENCE GROUNDING RULES" in v3
    assert "NEVER invent or hallucinate quotations" in v3
    assert "Check error handling" in v3

    # Dispatcher test
    assert build_prompt_by_version("v1", sub_text) == build_prompt_v1(sub_text, "Custom")
    assert build_prompt_by_version("v3", sub_text) == build_prompt_v3(sub_text, "Custom")


def test_clean_json_text() -> None:
    """Verify stripping of markdown json code fences."""
    raw = '```json\n{"key": "value"}\n```'
    assert clean_json_text(raw) == '{"key": "value"}'

    raw2 = '{"key": "value"}'
    assert clean_json_text(raw2) == '{"key": "value"}'


def test_criteria_schema_validation_and_deduplication() -> None:
    """Verify schema validation and case-insensitive deduplication of criteria."""
    valid_data = {
        "criteria": [
            {
                "name": "Code Modularity",
                "description": "Evaluates functions and separation of concerns.",
                "why_it_matters": "Enables maintainability.",
                "max_marks": 5.0,
                "evidence_guidance": "Look at function length.",
                "evidence_excerpt": "def calculate_tax",
                "evidence_location": "L1",
                "scoring_guidance": "5 for single-responsibility functions.",
                "order_index": 0,
            },
            {
                "name": "code modularity",  # Duplicate name with different casing
                "description": "Duplicate criterion",
                "why_it_matters": "...",
                "max_marks": 5.0,
            },
            {
                "name": "Documentation",
                "description": "Evaluates docstrings and inline comments.",
                "max_marks": 5.0,
            },
        ],
        "limitation_note": None,
        "prompt_version": "V3",
    }

    parsed = CriteriaProposalResponse.model_validate(valid_data)
    # Duplicate should be filtered out
    assert len(parsed.criteria) == 2
    assert parsed.criteria[0].name == "Code Modularity"
    assert parsed.criteria[1].name == "Documentation"


def test_criteria_schema_rejects_empty_list() -> None:
    """Verify that response without any criteria raises ValidationError."""
    with pytest.raises(ValidationError):
        CriteriaProposalResponse.model_validate({"criteria": []})


def test_missing_key_raises_value_error() -> None:
    """Verify that attempting generation without a key raises clear ValueError."""
    client_manager = GeminiClientManager(api_key=None)
    with pytest.raises(ValueError) as excinfo:
        generate_criteria(client_manager, "some code", "Code")
    assert "Add your Gemini API key in Settings" in str(excinfo.value)


def test_empty_submission_raises_value_error() -> None:
    """Verify that empty submission text is rejected."""
    client_manager = GeminiClientManager(api_key="AIzaSyDummyKey123456789")
    with pytest.raises(ValueError) as excinfo:
        generate_criteria(client_manager, "   ", "Code")
    assert "Cannot generate criteria for an empty submission" in str(excinfo.value)


@patch("google.genai.Client")
def test_mocked_gemini_generation_success(mock_client_class: MagicMock) -> None:
    """Verify end-to-end criteria generation with mocked Gemini response."""
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.text = json.dumps(
        {
            "criteria": [
                {
                    "name": "Algorithmic Efficiency",
                    "description": "Evaluates runtime time and space complexity.",
                    "why_it_matters": "Prevents slow execution.",
                    "max_marks": 5.0,
                    "evidence_guidance": "Inspect loops.",
                    "evidence_excerpt": "for item in data:",
                    "evidence_location": "L15",
                    "scoring_guidance": "5 for O(N), 2 for O(N^2).",
                }
            ],
            "limitation_note": None,
            "prompt_version": "V3",
        }
    )
    mock_instance.models.generate_content.return_value = mock_response

    manager = GeminiClientManager(api_key="AIzaSyValidDummyKey123456789")
    result = generate_criteria(
        client_manager=manager,
        submission_text="for item in data:\n    process(item)",
        submission_type="Code",
        prompt_version="V3",
    )

    assert len(result.criteria) == 1
    assert result.criteria[0].name == "Algorithmic Efficiency"
    assert result.criteria[0].evidence_excerpt == "for item in data:"
    assert result.criteria[0].evidence_location == "L15"


@patch("google.genai.Client")
def test_mocked_gemini_invalid_json(mock_client_class: MagicMock) -> None:
    """Verify that unparseable JSON from Gemini raises a clear ValueError."""
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    mock_response = MagicMock()
    mock_response.text = "NOT JSON AT ALL"
    mock_instance.models.generate_content.return_value = mock_response

    manager = GeminiClientManager(api_key="AIzaSyValidDummyKey123456789")
    with pytest.raises(ValueError) as excinfo:
        generate_criteria(
            client_manager=manager,
            submission_text="code here",
            submission_type="Code",
        )
    assert "Gemini returned an invalid JSON response" in str(excinfo.value)

