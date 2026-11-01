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

    # Basic Access Gate for 5-Person Prototype
    if settings.access_password and not st.session_state.get("authenticated", False):
        st.markdown(
            """
            <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
                <h1 style="color: #1e3a8a; margin-bottom: 0.25rem;">⚖️ EvalLens</h1>
                <p style="color: #64748b; font-size: 1.1rem;">Human and AI Evaluation Comparison Tool</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_left, col_mid, col_right = st.columns([1, 2, 1])
        with col_mid:
            st.info(
                "🔒 **Private 5-Person Testing Prototype**\n\n"
                "Welcome to the EvalLens testing workspace. This environment is shared among exactly 5 trusted testers. "
                "Evaluations, submissions, and rubrics are visible across testers in this shared workspace. "
                "Please do not submit confidential or sensitive personal information."
            )

            with st.form("access_gate_form"):
                pwd_input = st.text_input("Access Password", type="password", placeholder="Enter prototype password...")
                submit_btn = st.form_submit_button("Access Workspace", type="primary", use_container_width=True)

                if submit_btn:
                    if pwd_input.strip() == settings.access_password:
                        st.session_state["authenticated"] = True
                        st.success("Access granted!")
                        st.rerun()
                    else:
                        st.error("Incorrect password. Please contact the prototype administrator.")

        st.stop()

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
    if settings.access_password:
        st.sidebar.markdown(
            "🔒 **Tester Workspace**  \n"
            "<small style='color: #64748b;'>Shared environment for 5 testers</small>",
            unsafe_allow_html=True,
        )
        if st.sidebar.button("Lock / Sign Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()
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
