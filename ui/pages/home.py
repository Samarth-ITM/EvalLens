"""
Home page view for EvalLens.
"""

from __future__ import annotations

import streamlit as st
from database.db import get_evaluations_summary


def render_home_page() -> None:
    """Render the Home view."""
    st.subheader("Overview")
    st.write(
        "EvalLens helps you evaluate submitted work consistently by combining "
        "structured human judgment with automated AI rubric scoring."
    )

    # Primary action to start a new evaluation
    col1, _ = st.columns([1, 2])
    with col1:
        if st.button("Start New Evaluation", type="primary", use_container_width=True):
            st.session_state["active_nav"] = "New Evaluation"
            st.rerun()

    st.write("")
    st.subheader("Recent Evaluations")

    try:
        evaluations = get_evaluations_summary()
    except Exception as e:
        st.error(f"Could not load evaluations from the database: {e}")
        return

    if not evaluations:
        st.info("No evaluations yet.")
        st.caption("When you create evaluations and approve rubrics, they will be listed here.")
    else:
        for ev in evaluations[:5]:
            with st.container():
                st.markdown(
                    f"**{ev['title']}** — Type: `{ev['submission_type']}` | Status: `{ev['status']}`"
                )
                if ev["description"]:
                    st.write(ev["description"])
                st.caption(
                    f"Words: {ev['total_words']:,} | Created: {ev['created_at']}"
                )
                st.markdown("---")
