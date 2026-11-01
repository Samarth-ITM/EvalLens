"""
Unit tests for Gemini AI client and BYOK security.
Verifies Requirement 5: Missing Gemini key is handled safely.
"""

from __future__ import annotations

from core.ai_client import GeminiClientManager, mask_api_key, sanitize_error_message


def test_missing_key_handled_safely() -> None:
    """Verify that absent API key returns a safe error without crashing."""
    manager = GeminiClientManager(api_key=None)
    assert not manager.has_key
    assert manager.masked_key == ""

    # Test connection when key is missing
    success, message = manager.test_connection()
    assert success is False
    assert "Add your Gemini API key" in message


def test_empty_string_key_handled_safely() -> None:
    """Verify that whitespace/empty string key is treated as missing."""
    manager = GeminiClientManager(api_key="   ")
    assert not manager.has_key
    success, message = manager.test_connection()
    assert success is False
    assert "Add your Gemini API key" in message


def test_key_masking() -> None:
    """Verify masking never exposes the complete key."""
    assert mask_api_key(None) == ""
    assert mask_api_key("") == ""
    assert mask_api_key("short") == "••••••••"

    sample_key = "AIzaSyDummyKeyForTestingOnly9876543210"
    masked = mask_api_key(sample_key)
    assert masked.startswith("AIza")
    assert masked.endswith("3210")
    assert "DummyKeyForTestingOnly" not in masked
    assert len(masked) < len(sample_key)


def test_sanitize_error_message_strips_key() -> None:
    """Verify that exception messages containing the raw key are sanitized."""
    dummy_key = "AIzaSySecretLeakKey123456"
    leak_exception = Exception(f"HTTP 400: Call failed with key {dummy_key}")
    sanitized = sanitize_error_message(leak_exception, api_key=dummy_key)

    assert dummy_key not in sanitized
    assert "The provided Gemini API key is not valid" in sanitized or "couldn't connect" in sanitized


def test_client_manager_key_lifecycle() -> None:
    """Verify setting and clearing the API key in memory."""
    manager = GeminiClientManager()
    assert not manager.has_key

    manager.set_key("AIzaSyValidFormatKey123456789")
    assert manager.has_key
    assert "••••••••" in manager.masked_key

    manager.clear_key()
    assert not manager.has_key
    assert manager.masked_key == ""

