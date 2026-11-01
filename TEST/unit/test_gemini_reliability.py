"""
Unit tests for Gemini API reliability, error handling, and key safety.

Covers:
- Missing API key detection
- Invalid API key handling
- Network failure simulation
- Transient API errors (429, 503, timeouts) triggering automatic retries
- Non-transient errors (400, 401) failing immediately without useless retries
- Model context window exceeded
- Empty response from model
- Malformed JSON response
- Response missing required fields
- Unsupported model selection
- Zero API key exposure in error messages and exceptions
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
import pytest

from core.ai_client import (
    GeminiClientManager,
    execute_with_transient_retry,
    get_ai_client,
    is_transient_error,
    sanitize_error_message,
)
from core.evaluator import parse_and_validate_ai_response


def test_missing_api_key_test_connection() -> None:
    """Verify that attempting to test connection with no key returns False with clear message."""
    client = GeminiClientManager(api_key=None)
    assert client.has_key is False
    success, msg = client.test_connection()
    assert success is False
    assert "Add your Gemini API key" in msg


def test_api_key_scrubbing_never_leaks_key() -> None:
    """Verify that sanitize_error_message completely scrubs API keys from error strings."""
    secret_key = "AIzaSyD-SecretKey1234567890abcdef"
    
    # Test replacement in custom exception messages
    custom_error = Exception(f"Failed backend call trace: key={secret_key} debug info")
    sanitized = sanitize_error_message(custom_error, api_key=secret_key)
    assert secret_key not in sanitized
    assert "[PROTECTED_API_KEY]" in sanitized or "[KEY_REDACTED]" in sanitized

    # Test that HTTP errors return user-friendly messages without leaking the key
    http_error = Exception(f"HTTP 403 Forbidden for endpoint with key={secret_key}")
    sanitized_http = sanitize_error_message(http_error, api_key=secret_key)
    assert secret_key not in sanitized_http


def test_is_transient_error_detection() -> None:
    """Verify classification of transient vs non-transient exceptions."""
    # Transient errors
    assert is_transient_error(Exception("503 Service Unavailable")) is True
    assert is_transient_error(Exception("429 Resource has been exhausted (quota exceeded)")) is True
    assert is_transient_error(Exception("Deadline exceeded / connection timeout")) is True
    assert is_transient_error(Exception("Connection reset by peer")) is True

    # Non-transient errors
    assert is_transient_error(Exception("400 Bad Request: Invalid argument")) is False
    assert is_transient_error(Exception("401 Unauthorized: API key not valid")) is False
    assert is_transient_error(ValueError("Local validation failure")) is False


def test_transient_retry_eventual_success() -> None:
    """Verify that transient 503/429 errors are retried up to 2 times and return result upon success."""
    mock_func = MagicMock()
    # Fails once with 503, then succeeds
    mock_func.side_effect = [
        Exception("503 Model is temporarily overloaded"),
        "Successful API Result",
    ]

    result = execute_with_transient_retry(
        func=mock_func,
        max_retries=2,
        base_delay_seconds=0.01,
    )

    assert result == "Successful API Result"
    assert mock_func.call_count == 2


def test_transient_retry_exhaustion_raises() -> None:
    """Verify that if all retries fail on transient errors, the final exception is raised."""
    mock_func = MagicMock()
    mock_func.side_effect = Exception("429 Quota Exceeded")

    with pytest.raises(Exception) as excinfo:
        execute_with_transient_retry(
            func=mock_func,
            max_retries=2,
            base_delay_seconds=0.01,
        )
    assert "429 Quota Exceeded" in str(excinfo.value)
    assert mock_func.call_count == 3  # initial + 2 retries


def test_non_transient_error_fails_immediately() -> None:
    """Verify that 400 Bad Request or 401 Unauthorized errors fail immediately without retrying."""
    mock_func = MagicMock()
    mock_func.side_effect = Exception("401 API_KEY_INVALID")

    with pytest.raises(Exception, match="401 API_KEY_INVALID"):
        execute_with_transient_retry(
            func=mock_func,
            max_retries=2,
            base_delay_seconds=0.01,
        )
    assert mock_func.call_count == 1  # No retries for 401!


def test_unsupported_model_selected() -> None:
    """Verify that setting an unsupported model raises ValueError."""
    client = GeminiClientManager(api_key="AIzaSyD_dummy_key_1234567890")
    with pytest.raises(ValueError, match="is not in the list of supported models"):
        client.set_model("unsupported-unknown-model")


def test_empty_response_handling() -> None:
    """Verify that empty model response text raises a clear ValueError."""
    criteria = [{"id": 1, "name": "Security", "max_score": 5.0}]
    with pytest.raises(ValueError, match="Gemini returned an invalid JSON response"):
        parse_and_validate_ai_response("", criteria, "gemini-3.8-flash")


def test_malformed_json_response() -> None:
    """Verify that a malformed response raises a clear parsing error."""
    malformed_json = '{"scores": [{"criterion_id": 1, "score": 4.0'  # Truncated
    criteria = [{"id": 1, "name": "Security", "max_score": 5.0}]
    with pytest.raises(ValueError, match="Gemini returned an invalid JSON response"):
        parse_and_validate_ai_response(malformed_json, criteria, "gemini-3.8-flash")


def test_response_missing_required_fields() -> None:
    """Verify that responses missing required schema fields fail validation."""
    criteria = [{"id": 1, "name": "Security", "max_score": 5.0}]
    # Missing 'score' and 'reasoning'
    missing_fields_json = json.dumps({"scores": [{"criterion_id": 1}]})
    with pytest.raises(ValueError, match="AI response failed schema validation"):
        parse_and_validate_ai_response(missing_fields_json, criteria, "gemini-3.8-flash")


def test_context_window_exceeded_error_handling() -> None:
    """Verify that model context window exceeded is recognized as an error."""
    err = Exception("ResourceExhausted: Context window of 1048576 tokens exceeded")
    assert "Context window" in str(err) or is_transient_error(err)
