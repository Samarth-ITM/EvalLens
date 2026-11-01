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

                score_info = []
                if ev["human_total_score"] is not None:
                    score_info.append(f"Human: {ev['human_total_score']:.1f}")
                if ev["ai_total_score"] is not None:
                    score_info.append(f"AI: {ev['ai_total_score']:.1f}")

                score_str = f" | Scores: {', '.join(score_info)}" if score_info else ""
                st.caption(
                    f"Words: {ev['total_words']:,}{score_str} | Created: {ev['created_at']}"
                )

                if ev["approved_total_marks"] is not None:
                    if st.button("Evaluate / Compare ➔", key=f"home_eval_{ev['id']}"):
                        st.session_state["selected_eval_id"] = ev["id"]
                        st.session_state["active_nav"] = "Evaluate"
                        st.rerun()

                st.markdown("---")
