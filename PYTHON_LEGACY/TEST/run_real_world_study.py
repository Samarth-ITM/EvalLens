"""
Comprehensive Real-World Evaluation Study and Independent Quality Audit.
Executes the full evaluation pipeline across real-world corpus documents,
tests 5,000-word boundary limits, audits evidence grounding, and calculates statistics.
"""

from __future__ import annotations

import difflib
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config.settings import settings
from core.ai_client import GeminiClientManager
from core.comparison import calculate_comparison
from core.criteria_generator import generate_criteria
from core.document_parser import parse_uploaded_file
from core.evaluator import execute_ai_evaluation, submit_human_evaluation
from core.submission import check_submission_word_limit, prepare_submission, save_submission_to_db
from database import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RealWorldStudy")

CORPUS_DIR = Path("TEST/real_world_corpus")
MANIFEST_PATH = CORPUS_DIR / "corpus_manifest.json"
HUMAN_REF_PATH = Path("TEST/human_reference_evaluations.json")
OUTPUT_PATH = Path("TEST/real_world_study_results.json")


def clean_text_for_search(text: str) -> str:
    """Normalize whitespace and remove non-alphanumeric chars for robust substring matching."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", text)).strip().lower()


def audit_evidence_grounding(raw_text: str, evidence_text: str, evidence_location: str) -> Dict[str, Any]:
    """
    Audit whether an AI-cited evidence passage is grounded in the document text.
    Checks verbatim substring match, normalized fuzzy match, and line location.
    """
    if not evidence_text or evidence_text.strip() == "Missing evidence in submission.":
        return {
            "grounding_status": "missing_evidence_declared",
            "verbatim_match": False,
            "normalized_match": False,
            "line_accuracy": "n/a",
            "audit_note": "AI explicitly declared evidence was missing in submission.",
        }

    # Split multiline or ellipsis-separated excerpts
    excerpts = [p.strip() for p in re.split(r"\n\.\.\.\n|\.\.\.", evidence_text) if len(p.strip()) > 15]
    if not excerpts:
        excerpts = [evidence_text.strip()]

    raw_clean = clean_text_for_search(raw_text)
    raw_lines = raw_text.splitlines()

    matches = []
    for excerpt in excerpts:
        # 1. Exact verbatim match
        if excerpt in raw_text:
            matches.append("exact_verbatim")
            continue
        # 2. Normalized match
        exc_clean = clean_text_for_search(excerpt)
        if exc_clean and exc_clean in raw_clean:
            matches.append("normalized_verbatim")
            continue
        # 3. Fuzzy search for partial match
        words = exc_clean.split()
        if len(words) >= 5:
            prefix = " ".join(words[:6])
            if prefix in raw_clean:
                matches.append("prefix_match")
                continue
        matches.append("unmatched")

    is_grounded = any(m in ("exact_verbatim", "normalized_verbatim", "prefix_match") for m in matches)

    # Line number check
    line_accuracy = "unverified"
    line_match = re.search(r"L(\d+)(?:-L?(\d+))?", evidence_location or "")
    if line_match:
        start_line = int(line_match.group(1))
        # Check a window around start_line in raw_lines
        window_start = max(0, start_line - 15)
        window_end = min(len(raw_lines), start_line + 25)
        window_text = clean_text_for_search(" ".join(raw_lines[window_start:window_end]))
        exc_sample = clean_text_for_search(" ".join(excerpts[0].split()[:5]))
        if exc_sample in window_text:
            line_accuracy = "accurate"
        else:
            line_accuracy = "approximate_or_shifted"

    return {
        "grounding_status": "grounded" if is_grounded else "unverified_or_hallucinated",
        "verbatim_match": all(m == "exact_verbatim" for m in matches),
        "normalized_match": is_grounded,
        "line_accuracy": line_accuracy,
        "match_details": matches,
        "audit_note": "Evidence verified in document" if is_grounded else "Evidence passage not found verbatim in extracted text",
    }


def main():
    logger.info("Initializing Real-World Study Runner...")
    db.init_db()

    api_key = settings.get_effective_gemini_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not available in environment.")
    client_mgr = GeminiClientManager(api_key=api_key)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest_by_id = {d["id"]: d for d in manifest}

    with open(HUMAN_REF_PATH, "r", encoding="utf-8") as f:
        human_refs = json.load(f)

    study_results: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_used": client_mgr.model_name,
        "total_corpus_documents": len(manifest),
        "benchmark_evaluations": [],
        "boundary_tests": [],
        "format_extraction_summary": [],
        "aggregate_metrics": {},
    }

    # =========================================================================
    # PART 1: INGESTION AND EXTRACTION FIDELITY ACROSS ALL 23 DOCUMENTS
    # =========================================================================
    logger.info("--- PART 1: Ingestion & Extraction Verification Across 23 Documents ---")
    for item in manifest:
        doc_path = CORPUS_DIR / item["filename"]
        with open(doc_path, "rb") as f:
            data = f.read()

        t0 = time.time()
        parsed = parse_uploaded_file(data, item["filename"])
        parse_duration = time.time() - t0

        study_results["format_extraction_summary"].append({
            "id": item["id"],
            "filename": item["filename"],
            "format": item["format"],
            "domain": item["domain"],
            "file_size_bytes": len(data),
            "word_count": parsed.word_count,
            "line_count": parsed.line_count,
            "page_count": parsed.page_count,
            "parse_time_ms": round(parse_duration * 1000, 2),
            "warnings_count": len(parsed.warnings),
            "warnings": parsed.warnings,
            "extraction_status": "SUCCESS" if parsed.word_count > 0 else "EMPTY",
        })

    # =========================================================================
    # PART 2: 5,000-WORD BOUNDARY TESTING
    # =========================================================================
    logger.info("--- PART 2: 5,000-Word Boundary Testing ---")
    boundary_docs = ["DOC02", "DOC04", "DOC07", "DOC23"]
    for doc_id in boundary_docs:
        item = manifest_by_id[doc_id]
        doc_path = CORPUS_DIR / item["filename"]
        with open(doc_path, "rb") as f:
            data = f.read()

        parsed = parse_uploaded_file(data, item["filename"])
        is_valid, msg = check_submission_word_limit(parsed.word_count)

        # Attempt submission through prepare_submission
        caught_exception = False
        exception_msg = ""
        try:
            prepare_submission(
                title=f"Boundary Test: {item['title']}",
                submission_type="Boundary Test",
                uploaded_files=[(item["filename"], data)],
            )
        except ValueError as e:
            caught_exception = True
            exception_msg = str(e)

        boundary_result = {
            "document_id": doc_id,
            "filename": item["filename"],
            "format": item["format"],
            "word_count": parsed.word_count,
            "limit_enforced": not is_valid and caught_exception,
            "rejection_message": exception_msg,
            "verified_no_silent_truncation": caught_exception and (str(parsed.word_count) in exception_msg or f"{parsed.word_count:,}" in exception_msg),
        }
        study_results["boundary_tests"].append(boundary_result)
        logger.info(f"Boundary Test {doc_id} ({parsed.word_count} words): Rejection enforced={boundary_result['verified_no_silent_truncation']}")

    # =========================================================================
    # PART 3: FULL EVALUATION WORKFLOW ON 12 BENCHMARK DOCUMENTS
    # =========================================================================
    logger.info("--- PART 3: Complete Evaluation Workflow on 12 Benchmark Documents ---")
    all_criterion_comparisons = []
    all_evidence_audits = []

    for ref in human_refs:
        doc_id = ref["document_id"]
        logger.info(f"Evaluating {doc_id}: {ref['title']} ({ref['format']})...")
        doc_path = CORPUS_DIR / ref["filename"]
        with open(doc_path, "rb") as f:
            data = f.read()

        # 1. Ingestion
        t_start_ingest = time.time()
        prep = prepare_submission(
            title=ref["title"],
            submission_type=ref["domain"],
            uploaded_files=[(ref["filename"], data)],
            prompt_version="V3",
        )
        eval_id = save_submission_to_db(prep, uploaded_files_data=[(ref["filename"], data)])
        ingest_duration = time.time() - t_start_ingest

        # 2. Criteria Generation via Gemini
        t_start_gen = time.time()
        ai_proposal = generate_criteria(
            client_mgr,
            prep.combined_submission_text,
            submission_type=ref["domain"],
            prompt_version="V3",
        )
        gen_duration = time.time() - t_start_gen

        # Evaluate Criteria Quality
        generated_criteria_summary = [
            {
                "name": c.name,
                "description": c.description,
                "max_marks": c.max_marks,
                "evidence_guidance": c.evidence_guidance,
                "evidence_excerpt": c.evidence_excerpt,
                "evidence_location": c.evidence_location,
            }
            for c in ai_proposal.criteria
        ]

        # 3. Approve Human Reference Rubric
        criteria_to_save = [
            {
                "name": c["name"],
                "description": c["description"],
                "why_it_matters": "",
                "max_marks": c["max_score"],
                "evidence_guidance": c["scoring_guidance"],
                "evidence_excerpt": "",
                "evidence_location": "",
                "scoring_guidance": c["scoring_guidance"],
            }
            for c in ref["criteria"]
        ]
        db.save_approved_rubric(
            evaluation_id=eval_id,
            title=f"{ref['title']} Standard Rubric",
            description="Human Reference Rubric Benchmark",
            criteria=criteria_to_save,
            total_marks=ref["max_possible_score"],
        )

        rubric_data = db.get_rubric_with_criteria(eval_id)
        approved_criteria = rubric_data["criteria"]

        # 4. Submit Human Reference Scores
        human_scores_to_submit = []
        for idx, c in enumerate(approved_criteria):
            ref_c = ref["criteria"][idx]
            human_scores_to_submit.append({
                "criterion_id": c["id"],
                "criterion_name": c["name"],
                "score": ref_c["human_score"],
                "max_marks": c["max_score"],
                "feedback": ref_c["justification"],
            })
        submit_human_evaluation(
            evaluation_id=eval_id,
            scores=human_scores_to_submit,
            evaluator_name="Human Expert Reference",
        )

        # 5. Independent AI Evaluation
        t_start_eval = time.time()
        ai_scores = execute_ai_evaluation(
            client_manager=client_mgr,
            evaluation_id=eval_id,
            submission_text=prep.combined_submission_text,
            submission_type=ref["domain"],
            instructions=None,
            criteria=approved_criteria,
        )
        eval_duration = time.time() - t_start_eval

        # 6. Score Comparison
        h_scores_db = [dict(r) for r in db.get_human_scores(eval_id)]
        a_scores_db = [dict(r) for r in db.get_ai_scores(eval_id)]
        comparison = calculate_comparison(
            evaluation_id=eval_id,
            evaluation_title=ref["title"],
            criteria=[dict(c) for c in approved_criteria],
            human_scores=h_scores_db,
            ai_scores=a_scores_db,
            disagreement_threshold=10.0,
        )

        # 7. Evidence Grounding Audit on each criterion
        raw_doc_text = prep.documents[0].raw_text
        criterion_eval_details = []
        for cc in comparison.criteria_comparisons:
            audit = audit_evidence_grounding(
                raw_text=raw_doc_text,
                evidence_text=cc.ai_evidence_excerpt,
                evidence_location=cc.ai_evidence_location,
            )
            all_evidence_audits.append(audit)
            all_criterion_comparisons.append(cc)

            criterion_eval_details.append({
                "criterion_id": cc.criterion_id,
                "criterion_name": cc.criterion_name,
                "max_marks": cc.max_marks,
                "human_score": cc.human_score,
                "human_feedback": cc.human_feedback,
                "ai_score": cc.ai_score,
                "ai_reasoning": cc.ai_reasoning,
                "ai_evidence_excerpt": cc.ai_evidence_excerpt,
                "ai_evidence_location": cc.ai_evidence_location,
                "ai_uncertainty": cc.ai_uncertainty,
                "absolute_difference": cc.absolute_difference,
                "normalized_difference": cc.normalized_difference,
                "is_in_agreement": cc.is_in_agreement,
                "significant_disagreement": cc.significant_disagreement,
                "evidence_audit": audit,
            })

        # Calculate estimated cost (Gemini 3.5 Flash Lite: input ~$0.075/1M tok, output ~$0.30/1M tok)
        # Approximate tokens ~ word_count * 1.35
        est_input_tokens = int(prep.total_words * 1.35) + 800
        est_output_tokens = len(ai_scores) * 120 + 200
        est_cost_usd = round((est_input_tokens * 0.075 / 1_000_000) + (est_output_tokens * 0.30 / 1_000_000), 6)

        eval_summary = {
            "document_id": doc_id,
            "filename": ref["filename"],
            "title": ref["title"],
            "format": ref["format"],
            "domain": ref["domain"],
            "word_count": prep.total_words,
            "evaluation_id": eval_id,
            "performance_metrics": {
                "ingest_duration_s": round(ingest_duration, 3),
                "criteria_gen_duration_s": round(gen_duration, 2),
                "ai_evaluation_duration_s": round(eval_duration, 2),
                "est_input_tokens": est_input_tokens,
                "est_output_tokens": est_output_tokens,
                "est_cost_usd": est_cost_usd,
            },
            "criteria_generation": {
                "criteria_count": len(generated_criteria_summary),
                "criteria": generated_criteria_summary,
            },
            "comparison_summary": {
                "max_possible_marks": comparison.max_possible_marks,
                "human_total_marks": comparison.human_total_marks,
                "human_percentage": comparison.human_percentage,
                "ai_total_marks": comparison.ai_total_marks,
                "ai_percentage": comparison.ai_percentage,
                "total_difference": comparison.total_difference,
                "mae": comparison.mae,
                "agreement_percentage": comparison.agreement_percentage,
                "directional_bias": comparison.directional_bias,
                "criteria_count": len(criterion_eval_details),
            },
            "criteria_details": criterion_eval_details,
        }
        study_results["benchmark_evaluations"].append(eval_summary)
        logger.info(
            f"Finished {doc_id}: Human={comparison.human_total_marks}, AI={comparison.ai_total_marks}, "
            f"MAE={comparison.mae}%, Agreement={comparison.agreement_percentage}%, Eval Time={eval_duration:.1f}s"
        )

    # =========================================================================
    # PART 4: AGGREGATE STATISTICAL ANALYSIS
    # =========================================================================
    logger.info("--- PART 4: Calculating Aggregate Metrics ---")
    total_criteria = len(all_criterion_comparisons)
    exact_agreements = sum(1 for c in all_criterion_comparisons if c.absolute_difference == 0.0)
    close_agreements = sum(1 for c in all_criterion_comparisons if c.is_in_agreement)
    significant_disagreements = sum(1 for c in all_criterion_comparisons if c.significant_disagreement)
    moderate_divergences = total_criteria - close_agreements - significant_disagreements

    # Differences
    signed_diffs = [
        (c.ai_score - c.human_score) for c in all_criterion_comparisons if c.ai_score is not None
    ]
    abs_diffs = [
        c.absolute_difference for c in all_criterion_comparisons if c.absolute_difference is not None
    ]
    norm_diffs = [
        c.normalized_difference for c in all_criterion_comparisons if c.normalized_difference is not None
    ]

    mean_mae = round(sum(norm_diffs) / len(norm_diffs), 2) if norm_diffs else 0.0
    mean_bias = round(sum(signed_diffs) / len(signed_diffs), 2) if signed_diffs else 0.0
    overall_agreement_rate = round((close_agreements / total_criteria) * 100, 1) if total_criteria else 0.0

    # Evidence Grounding Audit Metrics
    grounded_evidence_count = sum(1 for a in all_evidence_audits if a["grounding_status"] == "grounded")
    verbatim_evidence_count = sum(1 for a in all_evidence_audits if a["verbatim_match"])
    accurate_line_count = sum(1 for a in all_evidence_audits if a["line_accuracy"] == "accurate")
    hallucination_count = sum(1 for a in all_evidence_audits if a["grounding_status"] == "unverified_or_hallucinated")

    study_results["aggregate_metrics"] = {
        "total_benchmark_documents": len(human_refs),
        "total_criteria_evaluated": total_criteria,
        "exact_agreement_count": exact_agreements,
        "exact_agreement_percentage": round((exact_agreements / total_criteria) * 100, 1),
        "close_agreement_count (<=10%)": close_agreements,
        "close_agreement_percentage": overall_agreement_rate,
        "moderate_divergence_count (10-25%)": moderate_divergences,
        "moderate_divergence_percentage": round((moderate_divergences / total_criteria) * 100, 1),
        "significant_disagreement_count (>25%)": significant_disagreements,
        "significant_disagreement_percentage": round((significant_disagreements / total_criteria) * 100, 1),
        "mean_absolute_error_percentage": mean_mae,
        "directional_bias_signed_mean": mean_bias,
        "bias_interpretation": "AI scores slightly higher on average (lenient)" if mean_bias > 0 else "AI scores slightly lower on average (harsh)",
        "evidence_grounding_audit": {
            "total_cited_passages": len(all_evidence_audits),
            "grounded_count": grounded_evidence_count,
            "grounding_rate_percentage": round((grounded_evidence_count / len(all_evidence_audits)) * 100, 1),
            "verbatim_match_count": verbatim_evidence_count,
            "accurate_line_reference_count": accurate_line_count,
            "hallucination_count": hallucination_count,
            "hallucination_rate_percentage": round((hallucination_count / len(all_evidence_audits)) * 100, 1),
        },
        "performance_and_cost": {
            "average_criteria_gen_latency_s": round(
                sum(b["performance_metrics"]["criteria_gen_duration_s"] for b in study_results["benchmark_evaluations"]) / len(human_refs), 2
            ),
            "average_evaluation_latency_s": round(
                sum(b["performance_metrics"]["ai_evaluation_duration_s"] for b in study_results["benchmark_evaluations"]) / len(human_refs), 2
            ),
            "total_estimated_cost_usd": round(
                sum(b["performance_metrics"]["est_cost_usd"] for b in study_results["benchmark_evaluations"]), 5
            ),
            "average_cost_per_document_usd": round(
                sum(b["performance_metrics"]["est_cost_usd"] for b in study_results["benchmark_evaluations"]) / len(human_refs), 5
            ),
        },
    }

    # Save to JSON
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(study_results, f, indent=2)

    logger.info(f"=== Study Complete! Results saved to {OUTPUT_PATH} ===")
    logger.info(f"Summary: Evaluated {len(human_refs)} docs, {total_criteria} criteria.")
    logger.info(f"Close Agreement Rate: {overall_agreement_rate}%, Mean MAE: {mean_mae}%, Bias: {mean_bias}")
    logger.info(f"Evidence Grounding Rate: {study_results['aggregate_metrics']['evidence_grounding_audit']['grounding_rate_percentage']}%")


if __name__ == "__main__":
    main()
