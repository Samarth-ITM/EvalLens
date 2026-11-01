"""
Evaluation History page view for EvalLens.
"""

from __future__ import annotations

import streamlit as st
from database.db import get_evaluations_summary


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
        st.write("Completed evaluation sessions will appear here once created.")
    else:
        st.write(f"Total evaluations recorded: **{len(evaluations)}**")
        for ev in evaluations:
            with st.expander(f"Evaluation #{ev['id']}: {ev['title']} ({ev['status']})"):
                st.write(f"**Description:** {ev['description'] or 'No description provided.'}")
                st.write(f"**Status:** `{ev['status']}`")
                st.write(f"**Created At:** {ev['created_at']}")
                st.write(f"**Last Updated:** {ev['updated_at']}")

