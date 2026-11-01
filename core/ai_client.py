"""
Gemini AI Client and BYOK (Bring Your Own Key) Management.

Handles API initialization, connection testing, key masking, error sanitization,
and safe, controlled retries for transient failures.
Strictly adheres to security guardrails: never logs, stores, or leaks API keys.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Optional, Tuple, TypeVar
from config.settings import settings
from core.validators import APIKeyValidation

logger = logging.getLogger(__name__)

T = TypeVar("T")


def mask_api_key(api_key: Optional[str]) -> str:
    """
    Mask an API key for safe UI display.
    Exposes only the first 4 and last 4 characters if sufficient length exists.
    """
    if not api_key:
        return ""
    key = api_key.strip()
    if len(key) <= 8:
        return "••••••••"
    return f"{key[:4]}••••••••{key[-4:]}"


def sanitize_error_message(err: Exception, api_key: Optional[str] = None) -> str:
    """
    Sanitize exception strings to ensure no API keys or internal secrets are revealed.
    """
    msg = str(err)
    if api_key and api_key.strip() in msg:
        msg = msg.replace(api_key.strip(), "[PROTECTED_API_KEY]")

    # Check for common Gemini error patterns and return user-friendly descriptions
    if "API key not valid" in msg or "400 INVALID_ARGUMENT" in msg:
        return "The provided Gemini API key is not valid. Please verify the key and try again."
    if "403" in msg or "PERMISSION_DENIED" in msg:
        return "Permission denied. Please ensure your Gemini API key has access to the chosen model."
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
        return "Gemini API rate limit reached or quota exceeded. Please try again later."
    if "Failed to establish a new connection" in msg or "ConnectionRefused" in msg:
        return "Could not connect to the Gemini service. Please check your internet connection."
    if "timed out" in msg.lower() or "timeout" in msg.lower():
        return "The request to Gemini timed out. Please try again."

    return f"We couldn't connect to Gemini: {msg}" if not ("AIza" in msg) else "We couldn't connect to Gemini. Check your API key and try again."


def is_transient_error(err: Exception) -> bool:
    """
    Determine whether an error is transient and eligible for a safe, limited retry.
    Transient errors: Rate limit (429), Server Error (500, 502, 503, 504), network timeouts.
    Non-transient errors: 400 (Bad Request), 401 (Invalid Key), 403 (Forbidden), schema/parse errors.
    """
    msg = str(err).lower()
    err_type = type(err).__name__.lower()

    # Explicit non-transient conditions (do NOT retry)
    if any(code in msg for code in ["400", "invalid_argument", "401", "unauthenticated", "403", "permission_denied"]):
        return False
    if isinstance(err, (ValueError, KeyError, TypeError)):
        return False

    # Transient indicators
    if any(code in msg for code in ["429", "resource_exhausted", "500", "502", "503", "504", "unavailable", "server error"]):
        return True
    if any(k in msg or k in err_type for k in ["timeout", "timed out", "connectionerror", "connection refused", "connection reset", "remoteprotocolerror"]):
        return True

    return False


def execute_with_transient_retry(
    func: Callable[[], T],
    max_retries: int = 2,
    base_delay_seconds: float = 0.5,
) -> T:
    """
    Execute a callable with controlled, limited exponential backoff for transient failures only.
    Non-transient failures are raised immediately without retrying.
    """
    attempts = 0
    while True:
        try:
            return func()
        except Exception as e:
            attempts += 1
            if attempts <= max_retries and is_transient_error(e):
                delay = base_delay_seconds * (2 ** (attempts - 1))
                logger.warning(
                    f"Transient failure detected ({type(e).__name__}). Retrying attempt {attempts}/{max_retries} after {delay:.2f}s..."
                )
                time.sleep(delay)
            else:
                # Re-raise non-transient error or exhausted retries
                raise


class GeminiClientManager:
    """
    Manages Gemini client instances and connection validation.
    Instances maintain credentials only in runtime memory.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None) -> None:
        self._api_key: Optional[str] = api_key.strip() if api_key and api_key.strip() else None
        self._model_name: str = model_name or settings.DEFAULT_MODEL

    @property
    def has_key(self) -> bool:
        """Check whether an API key is configured."""
        return bool(self._api_key)

    @property
    def masked_key(self) -> str:
        """Return the masked representation of the active API key."""
        return mask_api_key(self._api_key)

    @property
    def model_name(self) -> str:
        """Active Gemini model name."""
        return self._model_name

    def set_key(self, raw_key: str) -> None:
        """Validate and set a new API key in memory."""
        validated = APIKeyValidation(key=raw_key)
        self._api_key = validated.key

    def clear_key(self) -> None:
        """Remove the API key from memory."""
        self._api_key = None

    def set_model(self, model_name: str) -> None:
        """Update the selected Gemini model."""
        if model_name in settings.SUPPORTED_MODELS:
            self._model_name = model_name
        else:
            raise ValueError(f"Model {model_name} is not in the list of supported models.")

    def test_connection(self, model_override: Optional[str] = None) -> Tuple[bool, str]:
        """
        Execute a live API call to test connectivity and key validity with controlled retries.
        Returns (success_flag, user_message).
        """
        if not self._api_key:
            return False, "Add your Gemini API key to enable AI features."

        model_to_use = model_override or self._model_name

        try:
            from google import genai

            client = genai.Client(api_key=self._api_key)

            def _call() -> Any:
                return client.models.generate_content(
                    model=model_to_use,
                    contents="Ping",
                )

            response = execute_with_transient_retry(_call, max_retries=1, base_delay_seconds=0.3)
            if response and (hasattr(response, "text") or hasattr(response, "candidates")):
                return True, "Your Gemini connection is working."
            return False, "We received an unexpected response from Gemini. Please try again."

        except Exception as e:
            safe_msg = sanitize_error_message(e, self._api_key)
            return False, safe_msg


def get_ai_client(session_key: Optional[str] = None, model: Optional[str] = None) -> GeminiClientManager:
    """
    Factory to retrieve a client manager using the provided session key,
    or falling back to the environment configuration.
    """
    effective_key = settings.get_effective_gemini_api_key(session_key)
    effective_model = model or settings.DEFAULT_MODEL
    return GeminiClientManager(api_key=effective_key, model_name=effective_model)
