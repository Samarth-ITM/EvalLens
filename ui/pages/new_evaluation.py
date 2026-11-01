"""
New Evaluation page view for EvalLens.

Implements the Series 2 submission and criteria generation workflow:
- Document extraction and 5,000-word limit validation
- Gemini criteria proposal with evidence grounding
- Human rubric review, editing, reordering, and explicit approval
- Human-only manual rubric creation fallback
"""

from __future__ import annotations

import streamlit as st
from typing import List, Tuple

from config.settings import settings
from core.ai_client import GeminiClientManager
from core.criteria_generator import DEFAULT_PROMPT_VERSION, PROMPT_VERSIONS, generate_criteria
from core.document_parser import (
    MAX_SUBMISSION_WORDS,
    SUPPORTED_EXTENSIONS,
    check_submission_word_limit,
    count_words,
    parse_text_content,
    parse_uploaded_file,
)
from core.rubric import EditableCriterion, EditableRubric, approve_rubric, record_ai_proposal
from core.submission import PreparedSubmission, prepare_submission, save_submission_to_db
from core.validators import ALLOWED_SUBMISSION_TYPES


def reset_workflow() -> None:
    """Clear active submission session state."""
    st.session_state["eval_step"] = "setup"
    st.session_state["prepared_submission"] = None
    st.session_state["uploaded_files_data"] = []
    st.session_state["editable_rubric"] = None
    st.session_state["ai_limitation_note"] = None
    st.session_state["approved_eval_id"] = None


def init_state() -> None:
    """Initialize workflow state variables."""
    if "eval_step" not in st.session_state:
        st.session_state["eval_step"] = "setup"
    if "prepared_submission" not in st.session_state:
        st.session_state["prepared_submission"] = None
    if "uploaded_files_data" not in st.session_state:
        st.session_state["uploaded_files_data"] = []
    if "editable_rubric" not in st.session_state:
        st.session_state["editable_rubric"] = None
    if "ai_limitation_note" not in st.session_state:
        st.session_state["ai_limitation_note"] = None
    if "approved_eval_id" not in st.session_state:
        st.session_state["approved_eval_id"] = None


def render_new_evaluation_page() -> None:
    """Render the multi-step evaluation setup and rubric approval view."""
    init_state()
    step = st.session_state["eval_step"]

    st.subheader("New Evaluation")

    if step == "setup":
        render_setup_step()
    elif step == "review":
        render_review_step()
    elif step == "approved":
        render_approved_step()


# ----------------------------------------------------------------------
# Step 1: Submission Setup
# ----------------------------------------------------------------------

def render_setup_step() -> None:
    """Render the submission input form with live word counting and validation."""
    st.write(
        "Submit student or candidate work, select the evaluation type, and generate or create "
        "custom evaluation criteria."
    )

    with st.form("submission_form"):
        title = st.text_input(
            "Evaluation Title*",
            placeholder="e.g. CS101 Final Project Evaluation or Midterm Essay",
            help="A concise title to identify this evaluation session.",
        )

        col_type, col_prompt = st.columns([2, 1])
        with col_type:
            submission_type = st.selectbox(
                "Submission Type*",
                options=ALLOWED_SUBMISSION_TYPES,
                index=0,
                help="Select the category that best fits the submitted work.",
            )
        with col_prompt:
            prompt_version = st.selectbox(
                "AI Prompt Strategy",
                options=PROMPT_VERSIONS,
                index=PROMPT_VERSIONS.index(DEFAULT_PROMPT_VERSION),
                help="V3 is recommended (evidence-grounded with strict verification).",
            )

        instructions = st.text_area(
            "Evaluation Instructions (Optional)",
            placeholder="e.g. Focus on code modularity, edge case handling, and clarity of documentation.",
            help="Specific instructions or focus areas for the evaluation.",
        )

        reference_material = st.text_area(
            "Reference Material (Optional)",
            placeholder="e.g. Project assignment prompt, reference solution notes, or style guide.",
            help="Contextual material to guide the rubric. Kept separate from submitted work and not graded.",
        )

        st.markdown("#### Submission Content")
        st.caption("You can paste text, upload files, or combine both (up to 5,000 words total).")

        pasted_text = st.text_area(
            "Paste Submission Text",
            height=180,
            placeholder="Paste essay, code, or report text here...",
        )

        clean_exts = [ext.lstrip(".") for ext in sorted(SUPPORTED_EXTENSIONS)]
        uploaded_files = st.file_uploader(
            "Upload Files (Max 10 MB per file)",
            type=clean_exts,
            accept_multiple_files=True,
            help=f"Supported formats: {', '.join(clean_exts).upper()}",
        )

        st.markdown("---")
        col_ai, col_manual = st.columns([1, 1])
        with col_ai:
            submit_with_ai = st.form_submit_button(
                "Analyze with Gemini AI", type="primary", use_container_width=True
            )
        with col_manual:
            submit_manual = st.form_submit_button(
                "Create Rubric Manually (Human-Only)", use_container_width=True
            )

    # Process Form Submission
    if submit_with_ai or submit_manual:
        if not title.strip():
            st.error("Please provide an Evaluation Title.")
            return

        # Prepare uploaded files data
        files_data: List[Tuple[str, bytes]] = []
        if uploaded_files:
            for uf in uploaded_files:
                fbytes = uf.read()
                files_data.append((uf.name, fbytes))

        # Check that there is at least some content
        if not pasted_text.strip() and not files_data:
            st.error("Please provide submission content by pasting text or uploading at least one file.")
            return

        # Validate and prepare submission
        try:
            prepared = prepare_submission(
                title=title,
                submission_type=submission_type,
                instructions=instructions,
                reference_material=reference_material,
                pasted_text=pasted_text,
                uploaded_files=files_data,
                prompt_version=prompt_version,
            )
        except ValueError as e:
            st.error(str(e))
            return

        st.session_state["prepared_submission"] = prepared
        st.session_state["uploaded_files_data"] = files_data

        # If User chose AI Criteria Generation
        if submit_with_ai:
            api_key = st.session_state.get("gemini_api_key", settings.env_gemini_api_key)
            if not api_key:
                st.warning(
                    "No Gemini API key configured. You can add your API key in **Settings → AI Configuration**, "
                    "or click **Create Rubric Manually** to build the rubric without AI."
                )
                return

            selected_model = st.session_state.get("gemini_model", settings.DEFAULT_MODEL)
            client_manager = GeminiClientManager(api_key=api_key, model_name=selected_model)

            with st.spinner("Analyzing submission and generating evidence-grounded criteria with Gemini..."):
                try:
                    proposal = generate_criteria(
                        client_manager=client_manager,
                        submission_text=prepared.combined_submission_text,
                        submission_type=prepared.submission_type,
                        instructions=prepared.instructions,
                        reference_material=prepared.reference_material,
                        prompt_version=prepared.prompt_version,
                    )
                    editable = EditableRubric.from_ai_proposal(
                        proposal=proposal,
                        title=f"{prepared.title} Rubric",
                        description=f"Generated using {selected_model} ({prepared.prompt_version})",
                    )
                    st.session_state["editable_rubric"] = editable
                    st.session_state["ai_limitation_note"] = proposal.limitation_note
                    st.session_state["eval_step"] = "review"
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to generate criteria with Gemini: {e}")
                    st.info(
                        "You can continue by creating your rubric manually, or check your API key in Settings."
                    )
                    return

        # If User chose Manual Rubric Creation
        elif submit_manual:
            editable = EditableRubric(
                title=f"{prepared.title} Rubric",
                description="Custom human-created rubric",
                criteria=[],
                prompt_version="Manual",
            )
            # Add one default starter criterion
            editable.add_criterion(
                name="Content & Accuracy",
                description="Evaluates the accuracy, depth, and completeness of the submission.",
                max_marks=5.0,
            )
            st.session_state["editable_rubric"] = editable
            st.session_state["ai_limitation_note"] = None
            st.session_state["eval_step"] = "review"
            st.rerun()


# ----------------------------------------------------------------------
# Step 2: Rubric Review & Editing
# ----------------------------------------------------------------------

def render_review_step() -> None:
    """Render the interactive rubric editing, reordering, and approval view."""
    prepared: PreparedSubmission = st.session_state["prepared_submission"]
    rubric: EditableRubric = st.session_state["editable_rubric"]

    if not prepared or not rubric:
        st.session_state["eval_step"] = "setup"
        st.rerun()
        return

    # Header and Summary Banner
    st.markdown(f"### Review & Edit Rubric: *{prepared.title}*")
    st.write(
        "Review the proposed evaluation criteria below. You have complete control to edit names, "
        "descriptions, evidence guidance, maximum marks, or add and reorder criteria."
    )

    # Submission Metadata Card
    with st.expander("Submission Details & Extraction Summary", expanded=False):
        st.write(f"**Submission Type:** {prepared.submission_type}")
        st.write(f"**Total Word Count:** {prepared.total_words:,} words (Limit: 5,000 words)")
        st.write(f"**Files Included:** {len(prepared.documents)}")
        for doc in prepared.documents:
            st.markdown(f"- `{doc.filename}` ({doc.word_count:,} words)")
            if doc.warnings:
                for w in doc.warnings:
                    st.warning(f"Warning ({doc.filename}): {w}")

        if prepared.instructions:
            st.markdown(f"**Evaluator Instructions:**\n{prepared.instructions}")
        if prepared.reference_material:
            st.markdown(f"**Reference Material:**\n{prepared.reference_material}")

    # Display AI Limitation Note if Present
    if st.session_state.get("ai_limitation_note"):
        st.info(f"**Note from AI Analyzer:** {st.session_state['ai_limitation_note']}")

    # Total Marks Summary Bar
    st.markdown("---")
    col_tot, col_add, col_cancel = st.columns([2, 1, 1])
    with col_tot:
        st.markdown(
            f"#### Total Maximum Marks: **{rubric.total_marks:.1f}** "
            f"({len(rubric.criteria)} criteria)"
        )
    with col_add:
        if st.button("➕ Add Criterion", use_container_width=True):
            rubric.add_criterion(
                name="New Criterion",
                description="Describe the evaluation aspect...",
                max_marks=5.0,
            )
            st.rerun()
    with col_cancel:
        if st.button("Cancel / Restart", use_container_width=True):
            reset_workflow()
            st.rerun()

    # Criteria List Cards
    if not rubric.criteria:
        st.warning("No criteria currently in the rubric. Click 'Add Criterion' to add one.")
    else:
        for idx, crit in enumerate(rubric.criteria):
            with st.container():
                st.markdown(f"##### Criterion {idx+1}: **{crit.name}** ({crit.max_marks} marks)")

                c_col1, c_col2 = st.columns([3, 1])
                with c_col1:
                    new_name = st.text_input(
                        "Criterion Name",
                        value=crit.name,
                        key=f"crit_name_{idx}",
                    )
                    crit.name = new_name

                with c_col2:
                    new_marks = st.number_input(
                        "Max Marks",
                        min_value=0.5,
                        max_value=100.0,
                        value=float(crit.max_marks),
                        step=0.5,
                        key=f"crit_marks_{idx}",
                    )
                    crit.max_marks = new_marks

                new_desc = st.text_area(
                    "Description",
                    value=crit.description,
                    height=70,
                    key=f"crit_desc_{idx}",
                )
                crit.description = new_desc

                with st.expander("Evidence Guidance & Excerpt", expanded=False):
                    new_why = st.text_input(
                        "Why It Matters",
                        value=crit.why_it_matters,
                        key=f"crit_why_{idx}",
                    )
                    crit.why_it_matters = new_why

                    new_guidance = st.text_area(
                        "What Evidence to Inspect",
                        value=crit.evidence_guidance,
                        height=60,
                        key=f"crit_guidance_{idx}",
                    )
                    crit.evidence_guidance = new_guidance

                    # Evidence Grounding Display
                    if crit.evidence_excerpt:
                        loc_str = f" ({crit.evidence_location})" if crit.evidence_location else ""
                        st.markdown(f"**Grounded Submission Excerpt{loc_str}:**")
                        st.caption(f"\"{crit.evidence_excerpt}\"")

                    new_scoring = st.text_area(
                        "Scoring Guidance",
                        value=crit.scoring_guidance,
                        height=60,
                        key=f"crit_scoring_{idx}",
                    )
                    crit.scoring_guidance = new_scoring

                # Reordering & Deletion Controls
                btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 1, 3])
                with btn_col1:
                    if idx > 0 and st.button("⬆️ Up", key=f"up_{idx}"):
                        rubric.move_up(idx)
                        st.rerun()
                with btn_col2:
                    if idx < len(rubric.criteria) - 1 and st.button("⬇️ Down", key=f"down_{idx}"):
                        rubric.move_down(idx)
                        st.rerun()
                with btn_col3:
                    if st.button("🗑️ Delete", key=f"del_{idx}"):
                        rubric.remove_criterion(idx)
                        st.rerun()

                st.markdown("---")

    # Final Approval Action
    st.write("")
    approve_col, _ = st.columns([1, 1])
    with approve_col:
        if st.button("Approve Rubric", type="primary", use_container_width=True):
            if not rubric.criteria:
                st.error("You must have at least one criterion before approving.")
                return

            with st.spinner("Saving evaluation and approved rubric to database..."):
                try:
                    # 1. Save evaluation and submission files to DB & uploads/
                    eval_id = save_submission_to_db(
                        prepared=prepared,
                        uploaded_files_data=st.session_state.get("uploaded_files_data", []),
                    )

                    # 2. Record pristine AI proposal if this rubric originated from AI
                    if rubric.prompt_version != "Manual":
                        record_ai_proposal(
                            evaluation_id=eval_id,
                            proposal=st.session_state.get(
                                "last_ai_proposal",
                                CriteriaProposalResponse(
                                    criteria=[
                                        CriterionProposal(
                                            name=c.name,
                                            description=c.description,
                                            why_it_matters=c.why_it_matters,
                                            max_marks=c.max_marks,
                                            evidence_guidance=c.evidence_guidance,
                                            evidence_excerpt=c.evidence_excerpt,
                                            evidence_location=c.evidence_location,
                                            scoring_guidance=c.scoring_guidance,
                                        )
                                        for c in rubric.criteria
                                    ],
                                    prompt_version=rubric.prompt_version,
                                ),
                            ),
                        )

                    # 3. Save approved rubric to DB
                    rubric_id = approve_rubric(evaluation_id=eval_id, rubric=rubric)

                    st.session_state["approved_eval_id"] = eval_id
                    st.session_state["eval_step"] = "approved"
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to approve and save rubric: {e}")


# ----------------------------------------------------------------------
# Step 3: Approval Confirmation
# ----------------------------------------------------------------------

def render_approved_step() -> None:
    """Render confirmation of successful rubric approval."""
    eval_id = st.session_state.get("approved_eval_id")
    rubric: EditableRubric = st.session_state.get("editable_rubric")

    st.success("🎉 Rubric Approved and Saved Successfully!")
    st.write(
        f"Evaluation **#{eval_id}** is now established with an approved rubric and ready "
        f"for evaluation in Series 3."
    )

    if rubric:
        st.markdown(
            f"- **Approved Criteria:** {len(rubric.criteria)}\n"
            f"- **Total Marks:** {rubric.total_marks:.1f}\n"
            f"- **Strategy:** {rubric.prompt_version}"
        )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Score Evaluation ➔", type="primary", use_container_width=True):
            st.session_state["selected_eval_id"] = eval_id
            reset_workflow()
            st.session_state["active_nav"] = "Evaluate"
            st.rerun()
    with col2:
        if st.button("Start Another Evaluation", use_container_width=True):
            reset_workflow()
            st.rerun()
    with col3:
        if st.button("View in History", use_container_width=True):
            reset_workflow()
            st.session_state["active_nav"] = "Evaluation History"
            st.rerun()
