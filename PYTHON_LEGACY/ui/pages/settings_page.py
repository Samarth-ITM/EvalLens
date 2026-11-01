"""
Settings and AI Configuration page view for EvalLens.

Implements BYOK (Bring Your Own Key) management with session-only storage.
Ensures zero credential leakage and safe connection testing.
"""

from __future__ import annotations

import streamlit as st
from config.settings import settings
from core.ai_client import GeminiClientManager, mask_api_key
from core.validators import APIKeyValidation


def render_settings_page() -> None:
    """Render Settings and Gemini AI configuration."""
    st.subheader("Settings")
    st.write("Configure local application settings and AI model access.")

    st.markdown("### AI Configuration (Gemini BYOK)")
    st.write(
        "EvalLens follows a **Bring Your Own Key (BYOK)** approach. "
        "Enter your Google Gemini API key to enable automated rubric suggestions and AI scoring. "
        "If you do not have a key, you can still use all human-only evaluation workflows."
    )

    # Initialize session state variables if absent
    if "gemini_api_key" not in st.session_state:
        # Check if an environment variable fallback exists
        st.session_state["gemini_api_key"] = settings.env_gemini_api_key or ""
    if "gemini_model" not in st.session_state:
        st.session_state["gemini_model"] = settings.default_model
    if "connection_status" not in st.session_state:
        st.session_state["connection_status"] = None

    current_key = st.session_state["gemini_api_key"]

    # Model Selection
    selected_model = st.selectbox(
        "Gemini Model",
        options=settings.SUPPORTED_MODELS,
        index=settings.SUPPORTED_MODELS.index(st.session_state["gemini_model"])
        if st.session_state["gemini_model"] in settings.SUPPORTED_MODELS
        else 0,
        help="Select the Gemini model to use for rubric generation and scoring.",
    )
    st.session_state["gemini_model"] = selected_model

    # API Key Status Display
    st.write("#### Key Status")
    if current_key:
        is_env = (current_key == settings.env_gemini_api_key)
        source_label = "Loaded from .env environment" if is_env else "Session memory"
        st.success(f"Active Key: `{mask_api_key(current_key)}` ({source_label})")
    else:
        st.info("Add your Gemini API key to enable AI features.")

    # Key Input Field
    new_key_input = st.text_input(
        "Enter Gemini API Key",
        type="password",
        placeholder="Paste your Gemini API key here (e.g. AIzaSy...)",
        help="Your key is held strictly in session memory and is never saved to the database or written to disk.",
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Save Key", type="primary", use_container_width=True):
            if not new_key_input.strip():
                st.error("Please enter a non-empty API key.")
            else:
                try:
                    validated = APIKeyValidation(key=new_key_input)
                    st.session_state["gemini_api_key"] = validated.key
                    st.session_state["connection_status"] = None
                    st.success("API key saved to session memory.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Invalid API key format: {e}")

    with col2:
        if st.button("Test Connection", use_container_width=True):
            if not current_key and not new_key_input.strip():
                st.warning("Add your Gemini API key to enable AI features.")
            else:
                target_key = new_key_input.strip() if new_key_input.strip() else current_key
                with st.spinner("Testing connection to Gemini API..."):
                    manager = GeminiClientManager(api_key=target_key, model_name=selected_model)
                    is_ok, msg = manager.test_connection()
                    st.session_state["connection_status"] = (is_ok, msg)

    with col3:
        if st.button("Remove Key", use_container_width=True):
            st.session_state["gemini_api_key"] = ""
            st.session_state["connection_status"] = None
            st.info("API key removed from session memory.")
            st.rerun()

    # Display Connection Test Result if Available
    if st.session_state["connection_status"]:
        success, message = st.session_state["connection_status"]
        st.write("")
        if success:
            st.success(message)
        else:
            st.error(message)

    # Security & Persistence Notice
    st.markdown("---")
    st.caption(
        "**Privacy & Security Guardrails:**\n"
        "- Your API key is stored only in temporary server session memory.\n"
        "- The key is never persisted to the local SQLite database or shared in evaluation files.\n"
        "- If you restart the application, you may need to re-enter your key."
    )

