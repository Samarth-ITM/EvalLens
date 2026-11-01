"""
New Evaluation page view for EvalLens.
"""

from __future__ import annotations

import streamlit as st


def render_new_evaluation_page() -> None:
    """Render the New Evaluation setup view."""
    st.subheader("New Evaluation")
    st.write(
        "Here you will be able to upload documents or paste work to generate "
        "evaluation rubrics and compare human and AI scores."
    )

    st.info(
        "**Submission and AI criteria generation is scheduled for Series 2.**\n\n"
        "In the next development phase, this view will support:\n"
        "- Document and text upload processing\n"
        "- Automated Gemini criteria suggestions\n"
        "- Human rubric review, editing, and approval"
    )

    # Note explaining that workflow triggers are inactive in Series 1
    st.caption("Phase: Coming in a later development phase (Series 2).")

