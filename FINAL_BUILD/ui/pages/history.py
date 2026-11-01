"""
Evaluation History page view for EvalLens.

Displays previous evaluation sessions, submission details, approved rubrics,
and scoring comparison metrics stored in the local SQLite database.
"""

from __future__ import annotations

import streamlit as st
from database.db import (
    get_evaluations_summary,
    get_rubric_with_criteria,
    get_submissions_for_evaluation,
)


def render_history_page() -> None:
    """Render the Evaluation History view."""
    st.subheader("Evaluation History")
    st.write("Browse and review previous evaluation sessions stored in the local database.")

    try:
        evaluations = get_evaluations_summary()
    except Exception as e:
        st.error(f"Could not load evaluation history: {e}")
        return

    if not evaluations:
        st.info("No evaluations yet.")
        st.write("Completed evaluation sessions and approved rubrics will appear here once created.")
        return

    st.write(f"Total evaluations recorded: **{len(evaluations)}**")

    for ev in evaluations:
        status = ev["status"]
        if status == "completed":
            status_label = "✅ Evaluated & Compared"
        elif status == "human_evaluated":
            status_label = "👤 Human Evaluated"
        elif status == "rubric_approved":
            status_label = "📋 Rubric Approved"
        else:
            status_label = f"Status: `{status}`"

        expander_title = (
            f"Evaluation #{ev['id']}: {ev['title']} — {ev['submission_type']} ({status_label})"
        )

        with st.expander(expander_title):
            st.markdown(f"### {ev['title']}")
            if ev["description"]:
                st.caption(ev["description"])

            m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
            with m_col1:
                st.metric("Submission Type", ev["submission_type"])
            with m_col2:
                st.metric("Total Words", f"{ev['total_words']:,}")
            with m_col3:
                tot_marks = ev["approved_total_marks"]
                st.metric("Max Marks", f"{tot_marks:.1f}" if tot_marks is not None else "N/A")
            with m_col4:
                h_score = ev["human_total_score"]
                st.metric("Human Score", f"{h_score:.1f}" if h_score is not None else "Not scored")
            with m_col5:
                ai_score = ev["ai_total_score"]
                st.metric("AI Suggestion", f"{ai_score:.1f}" if ai_score is not None else "Not run")

            st.caption(f"Created: {ev['created_at']} | Strategy: {ev['prompt_version']}")

            # Quick Action Button to open in Evaluate
            if ev["approved_total_marks"] is not None:
                btn_label = "View Evaluation & Comparison ➔" if h_score is not None else "Score Evaluation ➔"
                if st.button(btn_label, key=f"eval_btn_{ev['id']}"):
                    st.session_state["selected_eval_id"] = ev["id"]
                    st.session_state["active_nav"] = "Evaluate"
                    st.rerun()

            # Display Submissions
            submissions = get_submissions_for_evaluation(ev["id"])
            if submissions:
                st.markdown("#### Submissions")
                for sub in submissions:
                    file_info = f" ({sub['file_type']})" if sub["file_type"] else ""
                    st.markdown(f"- **{sub['title']}**{file_info} — `{sub['word_count']:,} words`")
                    if sub["warnings"]:
                        st.warning(f"Warnings: {sub['warnings']}")

            # Display Approved Rubric
            rubric_data = get_rubric_with_criteria(ev["id"])
            if rubric_data:
                rubric = rubric_data["rubric"]
                criteria = rubric_data["criteria"]
                st.markdown("---")
                st.markdown(
                    f"#### Approved Rubric: *{rubric['title']}* "
                    f"({rubric['total_marks']:.1f} Total Marks)"
                )
                if rubric["description"]:
                    st.caption(rubric["description"])

                for c_idx, c in enumerate(criteria):
                    with st.container():
                        st.markdown(
                            f"**{c_idx+1}. {c['name']}** — `{c['max_score']} marks`"
                        )
                        st.write(c["description"])
                        if c["why_it_matters"]:
                            st.caption(f"*Why it matters:* {c['why_it_matters']}")
                        if c["evidence_guidance"]:
                            st.caption(f"*Evidence guidance:* {c['evidence_guidance']}")
                        if c["evidence_excerpt"]:
                            loc = f" [{c['evidence_location']}]" if c["evidence_location"] else ""
                            st.markdown(f"> *Excerpt{loc}:* \"{c['evidence_excerpt']}\"")
                        if c["scoring_guidance"]:
                            st.caption(f"*Scoring guidance:* {c['scoring_guidance']}")
                        st.markdown("---")
            else:
                st.info("No approved rubric yet for this evaluation.")
