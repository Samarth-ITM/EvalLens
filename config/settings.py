"""
EvalLens Configuration and Settings.

Manages application paths, environment variables, and configuration state
using pathlib for cross-platform portability.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Define base paths relative to the project root
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
UPLOADS_DIR: Path = BASE_DIR / "uploads"
DOCS_DIR: Path = BASE_DIR / "DOCS"
TEST_DIR: Path = BASE_DIR / "TEST"

# Automatically ensure local data and upload directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Load optional .env file from project root if it exists
ENV_FILE: Path = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)


class Settings:
    """Application settings and environment configuration."""

    PROJECT_NAME: str = "EvalLens"
    PROJECT_TAGLINE: str = "Human + AI Evaluation Workspace"
    APP_VERSION: str = "0.1.0 (Series 1 Foundation)"

    # Database configuration
    DB_NAME: str = "evallens.db"
    DEFAULT_DB_PATH: Path = DATA_DIR / DB_NAME

    # Supported Gemini models in the official google-genai SDK
    SUPPORTED_MODELS: list[str] = [
        "gemini-3.5-flash-lite",  # Default: cheapest, high-throughput model ($0.30/1M in, $2.50/1M out)
        "gemini-3.8-flash",       # Standard flash model
        "gemini-4-argon",         # Advanced reasoning model
    ]
    DEFAULT_MODEL: str = "gemini-3.5-flash-lite"

    def __init__(self) -> None:
        self.env: str = os.getenv("EVALLENS_ENV", "development").lower()
        custom_db = os.getenv("DB_PATH")
        if custom_db:
            custom_path = Path(custom_db)
            self.db_path = custom_path if custom_path.is_absolute() else (BASE_DIR / custom_path)
        else:
            self.db_path = self.DEFAULT_DB_PATH

        custom_uploads = os.getenv("UPLOADS_PATH")
        if custom_uploads:
            custom_u_path = Path(custom_uploads)
            self.uploads_dir = custom_u_path if custom_u_path.is_absolute() else (BASE_DIR / custom_u_path)
        else:
            self.uploads_dir = UPLOADS_DIR
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

        # Basic access password for private 5-person prototype
        is_hosted = self.env in ("production", "hosted", "render")
        raw_pwd = os.getenv("EVALLENS_ACCESS_PASSWORD")
        if is_hosted:
            if not raw_pwd or not raw_pwd.strip():
                raise ValueError(
                    f"EVALLENS_ACCESS_PASSWORD must be explicitly configured when EVALLENS_ENV is "
                    f"'{self.env}'. Unrestricted public access is prohibited in hosted deployments."
                )
            self.access_password: Optional[str] = raw_pwd.strip()
        else:
            default_pwd = "evallens2026"
            pwd_val = raw_pwd.strip() if raw_pwd is not None else default_pwd
            self.access_password = (
                None if pwd_val.lower() in ("", "none", "disable", "disabled", "false") else pwd_val
            )

        # Optional environment fallback for Gemini API key
        self._env_gemini_api_key: Optional[str] = (
            os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip() or None
        )
        self.default_model: str = os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL).strip()

    @property
    def env_gemini_api_key(self) -> Optional[str]:
        """Return the environment-provided Gemini API key if present."""
        return self._env_gemini_api_key

    def get_effective_gemini_api_key(self, session_key: Optional[str] = None) -> Optional[str]:
        """
        Returns the active API key.
        Session key (entered via UI) takes precedence over environment variable.
        """
        if session_key and session_key.strip():
            return session_key.strip()
        return self._env_gemini_api_key

    def __repr__(self) -> str:
        # Mask any sensitive details in string representation
        return (
            f"Settings(env={self.env!r}, db_path={str(self.db_path)!r}, "
            f"uploads_dir={str(self.uploads_dir)!r}, "
            f"has_access_password={bool(self.access_password)}, "
            f"has_env_api_key={bool(self._env_gemini_api_key)})"
        )


# Global singleton settings instance
settings = Settings()

