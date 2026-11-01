"""
Home page view for EvalLens.
"""

from __future__ import annotations

import streamlit as st
from core.document_parser import MAX_FILE_SIZE_BYTES, MAX_SUBMISSION_WORDS, SUPPORTED_EXTENSIONS, parse_uploaded_file
from core.submission import suggest_evaluation_title
from database.db import get_evaluations_summary


def render_home_page() -> None:
    """Render the Home view."""
    st.subheader("Start a New Evaluation")
    st.write(
        "Upload one document to begin a structured human evaluation with optional AI-assisted scoring."
    )

    clean_exts = [ext.lstrip(".") for ext in sorted(SUPPORTED_EXTENSIONS)]
    st.caption(
        f"Supported: {', '.join(clean_exts).upper()} · One document · "
        f"Maximum {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB · "
        f"Maximum {MAX_SUBMISSION_WORDS:,} extracted words"
    )
    with st.form("home_upload_form"):
        uploaded_file = st.file_uploader(
            "Upload a document to evaluate",
            type=clean_exts,
            accept_multiple_files=False,
            help="The original file is preserved. Scanned PDFs without extractable text are not supported.",
        )
        start_upload = st.form_submit_button("Continue with Document", type="primary")

    if start_upload:
        if not uploaded_file:
            st.error("Choose a document before continuing.")
        else:
            file_bytes = uploaded_file.getvalue()
            if len(file_bytes) > MAX_FILE_SIZE_BYTES:
                st.error("This document exceeds the 10 MB file-size limit.")
            else:
                try:
                    parsed = parse_uploaded_file(file_bytes, uploaded_file.name)
                except (ValueError, UnicodeError) as exc:
                    st.error(str(exc))
                else:
                    if parsed.warnings and not parsed.raw_text.strip():
                        st.error("This document could not be read: " + " ".join(parsed.warnings))
                    elif parsed.word_count > MAX_SUBMISSION_WORDS:
                        st.error(
                            f"This document contains {parsed.word_count:,} extracted words, exceeding the "
                            f"{MAX_SUBMISSION_WORDS:,}-word limit."
                        )
                    else:
                        st.session_state["pending_home_upload"] = [(uploaded_file.name, file_bytes)]
                        st.session_state["suggested_evaluation_title"] = suggest_evaluation_title(
                            uploaded_file.name, parsed.raw_text
                        )
                        st.session_state["eval_step"] = "setup"
                        st.session_state["active_nav"] = "New Evaluation"
                        st.rerun()

    st.write("")
    st.subheader("Past Evaluations")

    try:
        evaluations = get_evaluations_summary()
    except Exception as e:
        st.error(f"Could not load evaluations from the database: {e}")
        return

    if not evaluations:
        st.info("No evaluations yet. Upload a document above to start one.")
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
                    action = "View Read-Only Results ➔" if ev["status"] == "completed" else "Continue Evaluation ➔"
                    if st.button(action, key=f"home_eval_{ev['id']}"):
                        st.session_state["selected_eval_id"] = ev["id"]
                        st.session_state["active_nav"] = "Evaluate"
                        st.rerun()

                st.markdown("---")
