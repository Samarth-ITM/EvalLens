"""
EvalLens - Human and AI Evaluation Comparison Tool.

Main application entry point.
"""

from __future__ import annotations

from pathlib import Path
import streamlit as st

from config.settings import BASE_DIR, settings
from database.db import init_db
from ui.components.header import render_header
from ui.pages.evaluate import render_evaluate_page
from ui.pages.history import render_history_page
from ui.pages.home import render_home_page
from ui.pages.new_evaluation import render_new_evaluation_page
from ui.pages.settings_page import render_settings_page


def apply_custom_styles() -> None:
    """Load local CSS for consistent and professional styling."""
    css_file = BASE_DIR / "ui" / "styles" / "main.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main() -> None:
    """Application bootstrap and page routing."""
    st.set_page_config(
        page_title="EvalLens — Human + AI Evaluation Workspace",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize SQLite database automatically
    try:
        init_db()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        st.stop()

    # Load custom styles
    apply_custom_styles()

    # Navigation setup
    nav_options = ["Home", "New Evaluation", "Evaluate", "Evaluation History", "Settings"]

    if "active_nav" not in st.session_state:
        st.session_state["active_nav"] = "Home"

    # Sidebar Navigation
    st.sidebar.title("EvalLens")
    st.sidebar.caption("Navigation")

    selected_nav = st.sidebar.radio(
        label="Select View",
        options=nav_options,
        index=nav_options.index(st.session_state["active_nav"])
        if st.session_state["active_nav"] in nav_options
        else 0,
        label_visibility="collapsed",
    )
    st.session_state["active_nav"] = selected_nav

    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"**EvalLens v1.0.0**\n\n"
        "Human and AI Evaluation Comparison Tool\n\n"
        "AI assists evaluation; human controls the final result."
    )

    # Render persistent header
    render_header()

    # Route to selected page
    if selected_nav == "Home":
        render_home_page()
    elif selected_nav == "New Evaluation":
        render_new_evaluation_page()
    elif selected_nav == "Evaluate":
        render_evaluate_page()
    elif selected_nav == "Evaluation History":
        render_history_page()
    elif selected_nav == "Settings":
        render_settings_page()


if __name__ == "__main__":
    main()
