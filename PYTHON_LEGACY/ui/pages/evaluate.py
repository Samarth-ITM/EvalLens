"""
Evaluate and Comparison Dashboard view for EvalLens.

Implements Series 3:
- Human scoring interface with 0.5 increments and validation
- Independent optional AI evaluation using the exact approved rubric
- Strict Independence Rule: AI scores remain hidden until human submission is complete
- Comparison metrics: Normalized Differences, MAE, Agreement Percentage (10 pp tolerance)
- Simple, transparent side-by-side comparison dashboard
- Full human-only workflow support
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
from typing import Any, Dict, List, Optional

from config.settings import settings
from core.ai_client import GeminiClientManager
from core.comparison import calculate_comparison
from core.evaluator import execute_ai_evaluation, submit_human_evaluation
from database.db import (
    get_ai_scores,
    get_evaluation,
    get_evaluations_summary,
    get_human_scores,
    get_rubric_with_criteria,
    get_submissions_for_evaluation,
    has_ai_scores,
    has_human_scores,
)


def render_evaluate_page() -> None:
    """Render the scoring and evaluation comparison workspace."""
    st.subheader("Evaluation & Score Comparison")

    # Fetch available evaluations
    evaluations = get_evaluations_summary()
    if not evaluations:
        st.info("No evaluations available. Create an evaluation and approve a rubric first.")
        if st.button("Start New Evaluation", type="primary"):
            st.session_state["active_nav"] = "New Evaluation"
            st.rerun()
        return

    # Filter to evaluations that have at least an approved rubric
    approved_evals = [e for e in evaluations if e["approved_total_marks"] is not None]
    if not approved_evals:
        st.warning("No evaluations with an approved rubric found. Please approve a rubric first.")
        if st.button("Go to New Evaluation"):
            st.session_state["active_nav"] = "New Evaluation"
            st.rerun()
        return

    # Select Active Evaluation
    eval_options = {e["id"]: f"#{e['id']} — {e['title']} ({e['status']})" for e in approved_evals}
    default_id = st.session_state.get("selected_eval_id", approved_evals[0]["id"])
    if default_id not in eval_options:
        default_id = approved_evals[0]["id"]

    eval_keys = list(eval_options.keys())
    default_index = eval_keys.index(default_id)

    selected_eval_id = st.selectbox(
        "Select Evaluation Session",
        options=eval_keys,
        format_func=lambda x: eval_options[x],
        index=default_index,
    )
    st.session_state["selected_eval_id"] = selected_eval_id

    # Load evaluation and rubric data
    ev_record = get_evaluation(selected_eval_id)
    rubric_data = get_rubric_with_criteria(selected_eval_id)

    if not ev_record or not rubric_data:
        st.error("Failed to load evaluation rubric data.")
        return

    criteria = rubric_data["criteria"]
    rubric = rubric_data["rubric"]
    submissions = get_submissions_for_evaluation(selected_eval_id)

    # ------------------------------------------------------------------
    # Section A: Submission & Criteria Overview
    # ------------------------------------------------------------------
    with st.expander("Submission Content & Context", expanded=False):
        st.markdown(f"**Title:** {ev_record['title']}")
        st.markdown(f"**Submission Type:** `{ev_record['submission_type']}`")
        if ev_record["instructions"]:
            st.markdown(f"**Instructions:**\n{ev_record['instructions']}")
        if ev_record["reference_material"]:
            st.markdown(f"**Reference Material:**\n{ev_record['reference_material']}")

        st.markdown("#### Submissions")
        for sub in submissions:
            st.markdown(f"**Source: {sub['title']}** (`{sub['word_count']} words`)")
            st.text_area(
                f"Content ({sub['title']})",
                value=sub["content"],
                height=140,
                disabled=True,
                key=f"sub_content_{sub['id']}",
            )

    # Check status of evaluations
    is_human_done = has_human_scores(selected_eval_id)
    is_ai_done = has_ai_scores(selected_eval_id)
    is_completed = ev_record["status"] == "completed"

    if is_completed:
        st.info("🔒 This evaluation is completed and locked. You are viewing read-only historical results.")

    # Workflow progress breadcrumb
    if not is_human_done and not is_completed:
        st.caption("📍 **Progress:** `1. Human Scoring (In Progress)` ➔ 2. Optional AI Evaluation ➔ 3. Comparison Dashboard")
    elif not is_ai_done:
        st.caption("📍 **Progress:** 1. Human Scoring (Completed ✅) ➔ `2. Optional AI Evaluation (Ready)` ➔ 3. Comparison Dashboard")
    else:
        st.caption("📍 **Progress:** 1. Human Scoring (Completed ✅) ➔ 2. AI Evaluation (Completed ✅) ➔ `3. Comparison Dashboard Active 📊`")

    st.markdown("---")

    # ------------------------------------------------------------------
    # Section B: Human Evaluation (Scoring Form)
    # ------------------------------------------------------------------
    st.markdown("### 1. Human Evaluation")

    existing_human_scores = {
        int(row["criterion_id"]): row for row in get_human_scores(selected_eval_id)
    }

    if not is_human_done and not is_completed:
        st.write(
            "Enter your scores and qualitative remarks below. "
            "Scores must be between 0 and the criterion maximum (using 0.5 increments). "
            "**Independence Notice:** AI evaluation scores remain strictly hidden until you submit."
        )

        with st.form("human_scoring_form"):
            score_entries: List[Dict[str, Any]] = []

            for idx, crit in enumerate(criteria):
                c_id = crit["id"]
                max_score = float(crit["max_score"])
                prev_val = (
                    float(existing_human_scores[c_id]["score"])
                    if c_id in existing_human_scores
                    else 0.0
                )
                prev_feedback = (
                    existing_human_scores[c_id]["feedback"]
                    if c_id in existing_human_scores
                    else ""
                )

                st.markdown(f"##### {idx+1}. {crit['name']} *(Max: {max_score} marks)*")
                st.caption(crit["description"])

                if crit.get("evidence_guidance"):
                    st.caption(f"**Evidence to inspect:** {crit['evidence_guidance']}")

                if crit.get("evidence_excerpt"):
                    loc = f" [{crit['evidence_location']}]" if crit.get("evidence_location") else ""
                    st.markdown(f"> *Grounded Excerpt{loc}:* \"{crit['evidence_excerpt']}\"")

                col_score, col_comment = st.columns([1, 3])
                with col_score:
                    h_score = st.number_input(
                        f"Score (0 - {max_score})",
                        min_value=0.0,
                        max_value=max_score,
                        value=min(prev_val, max_score),
                        step=0.5,
                        key=f"h_score_{c_id}",
                    )
                with col_comment:
                    h_comment = st.text_input(
                        "Evaluator Remarks / Justification",
                        value=prev_feedback,
                        placeholder="Optional feedback on this criterion...",
                        key=f"h_comment_{c_id}",
                    )

                score_entries.append(
                    {
                        "criterion_id": c_id,
                        "criterion_name": crit["name"],
                        "score": h_score,
                        "max_marks": max_score,
                        "feedback": h_comment,
                    }
                )
                st.markdown("---")

            evaluator_name = st.text_input("Evaluator Name", value="Human Evaluator")

            col_sub1, col_sub2 = st.columns([1, 1])
            with col_sub1:
                submitted = st.form_submit_button(
                    "Submit Human Evaluation", type="primary", use_container_width=True
                )
            with col_sub2:
                saved_draft = st.form_submit_button(
                    "Save Progress", use_container_width=True
                )

        if submitted or saved_draft:
            try:
                submit_human_evaluation(
                    evaluation_id=selected_eval_id,
                    scores=score_entries,
                    evaluator_name=evaluator_name,
                )
                if submitted:
                    st.success("Human evaluation successfully submitted!")
                else:
                    st.info("Progress saved.")
                st.rerun()
            except ValueError as e:
                st.error(f"Validation error: {e}")

    else:
        # Human evaluation is complete
        human_rows = get_human_scores(selected_eval_id)
        h_total = sum(float(r["score"]) for r in human_rows)
        max_total = float(rubric["total_marks"])
        h_pct = round((h_total / max_total) * 100.0, 1) if max_total > 0 else 0.0

        st.success(
            f"✅ **Human Evaluation Completed** — Awarded: **{h_total:.1f} / {max_total:.1f}** ({h_pct}%)"
        )

        with st.expander("Review Human Scores", expanded=False):
            for r in human_rows:
                st.markdown(f"- **{r['criterion_name']}:** `{r['score']} / {r['max_score']}`")
                if r["feedback"]:
                    st.caption(f"Remarks: {r['feedback']}")

        if not is_completed and st.button("Edit Human Scores"):
            # Temporary state to allow modifying
            st.session_state[f"re_edit_human_{selected_eval_id}"] = True
            st.info("You can re-edit your scores above.")

    st.markdown("---")

    # ------------------------------------------------------------------
    # Section C: Optional AI Evaluation
    # ------------------------------------------------------------------
    st.markdown("### 2. Independent AI Evaluation")

    if not is_human_done:
        st.info(
            "🔒 **Independence Guardrail Active:**\n"
            "AI evaluation results and suggestions remain hidden until you complete and submit your human evaluation."
        )
    else:
        if is_ai_done:
            ai_rows = get_ai_scores(selected_eval_id)
            ai_total = sum(float(r["score"]) for r in ai_rows if r["score"] is not None)
            max_total = float(rubric["total_marks"])
            ai_pct = round((ai_total / max_total) * 100.0, 1) if max_total > 0 else 0.0
            model_used = ai_rows[0]["model_name"] if ai_rows else "Gemini"

            st.success(
                f"🤖 **AI Evaluation Completed** ({model_used}) — Suggested: **{ai_total:.1f} / {max_total:.1f}** ({ai_pct}%)"
            )

            col_rerun, _ = st.columns([1, 2])
            with col_rerun:
                if not is_completed and st.button("Re-run AI Evaluation"):
                    run_ai_eval_action(selected_eval_id, ev_record, submissions, criteria)
        else:
            st.write(
                "You have completed human evaluation. You can now optionally run an independent "
                "AI evaluation using Google Gemini on the approved rubric."
            )
            col_run, _ = st.columns([1, 2])
            with col_run:
                if not is_completed and st.button("Run AI Evaluation with Gemini", type="primary"):
                    run_ai_eval_action(selected_eval_id, ev_record, submissions, criteria)

    st.markdown("---")

    # ------------------------------------------------------------------
    # Section D: Comparison Dashboard
    # ------------------------------------------------------------------
    if is_human_done:
        st.markdown("### 3. Comparison Dashboard")

        human_data = [dict(r) for r in get_human_scores(selected_eval_id)]
        ai_data = [dict(r) for r in get_ai_scores(selected_eval_id)] if is_ai_done else None

        comparison = calculate_comparison(
            evaluation_id=selected_eval_id,
            evaluation_title=ev_record["title"],
            criteria=[dict(c) for c in criteria],
            human_scores=human_data,
            ai_scores=ai_data,
            disagreement_threshold=10.0,
        )

        # Overview Metrics Row
        if comparison.has_ai_evaluation:
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.metric("Human Total", f"{comparison.human_total_marks:.1f} / {comparison.max_possible_marks:.1f}", f"{comparison.human_percentage:.1f}%")
            with m2:
                ai_t = comparison.ai_total_marks or 0.0
                ai_p = comparison.ai_percentage or 0.0
                st.metric("AI Suggestion", f"{ai_t:.1f} / {comparison.max_possible_marks:.1f}", f"{ai_p:.1f}%")
            with m3:
                bias = comparison.directional_bias if comparison.directional_bias is not None else 0.0
                bias_label = "AI Higher" if bias > 0 else ("AI Lower" if bias < 0 else "Aligned")
                st.metric(
                    "Directional Bias",
                    f"{bias:+.1f} pts",
                    delta=bias_label,
                    delta_color="off",
                    help="Aggregate difference between AI and Human scores (AI Total - Human Total).",
                )
            with m4:
                st.metric(
                    "MAE (Normalized)",
                    f"{comparison.mae:.1f}%" if comparison.mae is not None else "N/A",
                    help="Mean Absolute Error across normalized criterion scores. Does NOT represent error against a ground truth.",
                )
            with m5:
                st.metric(
                    "Agreement Rate",
                    f"{comparison.agreement_percentage:.1f}%" if comparison.agreement_percentage is not None else "N/A",
                    help="Percentage of criteria with difference within 10 percentage points.",
                )

            # Visual Comparison Chart (Plotly)
            st.markdown("#### Score Comparison per Criterion")
            crit_names = [c.criterion_name for c in comparison.criteria_comparisons]
            h_scores = [c.human_score for c in comparison.criteria_comparisons]
            a_scores = [c.ai_score if c.ai_score is not None else None for c in comparison.criteria_comparisons]
            max_scores = [c.max_marks for c in comparison.criteria_comparisons]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=crit_names,
                y=h_scores,
                name="Human Score",
                marker_color="#2563eb",
            ))
            fig.add_trace(go.Bar(
                x=crit_names,
                y=a_scores,
                name="AI Suggestion",
                marker_color="#7c3aed",
            ))

            fig.update_layout(
                barmode="group",
                margin=dict(l=20, r=20, t=30, b=50),
                height=320,
                xaxis_title="Evaluation Criteria",
                yaxis_title="Score",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Detailed Comparison Table
            st.markdown("#### Criterion-Level Alignment Breakdown")
            for c in comparison.criteria_comparisons:
                if c.ai_score is not None:
                    ai_score_str = f"`{c.ai_score} / {c.max_marks}` ({c.ai_normalized}%)"
                    disagree_badge = "⚠️ Disagreement (>10% diff)" if c.significant_disagreement else "✅ Agreement"
                    diff_caption = f"Absolute Diff: {c.absolute_difference} marks | Normalized Diff: {c.normalized_difference}%"
                else:
                    ai_score_str = "`N/A (Missing evidence)`"
                    disagree_badge = "ℹ️ Missing Evidence"
                    diff_caption = "Excluded from MAE and Agreement metrics due to missing evidence."

                with st.expander(
                    f"{c.criterion_name}: Human `{c.human_score}` vs AI `{'N/A' if c.ai_score is None else c.ai_score}` ({disagree_badge})"
                ):
                    col_det1, col_det2 = st.columns(2)
                    with col_det1:
                        st.markdown(f"**Human Evaluation:** `{c.human_score} / {c.max_marks}` ({c.human_normalized}%)")
                        if c.human_feedback:
                            st.write(f"*Remarks:* {c.human_feedback}")
                        else:
                            st.caption("No specific remarks provided.")

                    with col_det2:
                        st.markdown(f"**AI Suggestion:** {ai_score_str}")
                        if c.ai_reasoning:
                            st.write(f"*Reasoning:* {c.ai_reasoning}")
                        if c.ai_evidence_excerpt:
                            loc = f" [{c.ai_evidence_location}]" if c.ai_evidence_location else ""
                            st.markdown(f"> *Evidence{loc}:* \"{c.ai_evidence_excerpt}\"")
                        if c.ai_uncertainty:
                            st.caption(f"*Uncertainty / Limitations:* {c.ai_uncertainty}")

                    st.caption(diff_caption)

            st.caption(
                "**Note on interpretation:** AI scores are independent suggestions to assist consistency. "
                "The human score is the authoritative final evaluation."
            )

        else:
            # Human-only evaluation view
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Human Total Score", f"{comparison.human_total_marks:.1f} / {comparison.max_possible_marks:.1f}")
            with m2:
                st.metric("Percentage", f"{comparison.human_percentage:.1f}%")

            st.info("AI evaluation was not run for this session. Showing human-only evaluation results.")
            for c in comparison.criteria_comparisons:
                st.markdown(f"- **{c.criterion_name}:** `{c.human_score} / {c.max_marks}` ({c.human_normalized}%)")
                if c.human_feedback:
                    st.caption(f"Remarks: {c.human_feedback}")


def run_ai_eval_action(
    eval_id: int,
    ev_record: Any,
    submissions: List[Any],
    criteria: List[Any],
) -> None:
    """Helper to execute AI evaluation."""
    api_key = st.session_state.get("gemini_api_key") or settings.env_gemini_api_key
    if not api_key:
        st.error(
            "No Gemini API key configured. Please enter your key in **Settings → AI Configuration** "
            "to run AI evaluation."
        )
        return

    combined_text = "\n\n".join(f"=== {s['title']} ===\n{s['content']}" for s in submissions)
    selected_model = st.session_state.get("gemini_model", settings.DEFAULT_MODEL)
    client_manager = GeminiClientManager(api_key=api_key, model_name=selected_model)

    with st.spinner("AI is evaluating submission against approved criteria..."):
        try:
            execute_ai_evaluation(
                client_manager=client_manager,
                evaluation_id=eval_id,
                submission_text=combined_text,
                submission_type=ev_record["submission_type"],
                instructions=ev_record["instructions"],
                criteria=[dict(c) for c in criteria],
            )
            st.success("AI evaluation complete!")
            st.rerun()
        except Exception as e:
            st.error(f"AI evaluation failed: {e}")

