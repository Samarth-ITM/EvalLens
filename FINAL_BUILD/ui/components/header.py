"""
Header component for EvalLens.
Establishes clear product identity across all views.
"""

from __future__ import annotations

import streamlit as st


def render_header() -> None:
    """Render the application header and product identity."""
    st.title("EvalLens")
    st.caption("Human + AI Evaluation Workspace")
    st.markdown("---")

