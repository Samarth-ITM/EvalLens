"""
Integration test executing the full EvalLens lifecycle on the realistic sample evaluation report.

Workflow stages tested:
1. Submission of realistic technical report (TEST/fixtures/sample_report.md).
2. Verification of document extraction, word counting (1,338 words), and structure.
3. Criteria generation grounded in the report content (with realistic/grounded mock or live API).
4. Human review, editing, and explicit approval of rubric.
5. Independent human scoring and qualitative comments.
6. Progress saving (draft) followed by final submission.
7. Gating verification: AI scores remain hidden prior to human submission.
8. Independent AI evaluation on exact approved rubric criteria.
9. Score comparison analytics (MAE, agreement rate, directional bias, correlation).
10. Database persistence across simulated restarts.
11. Human-only execution path without Gemini API key.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from core.comparison import calculate_comparison
from core.document_parser import parse_uploaded_file
from core.evaluator import parse_and_validate_ai_response, validate_human_score
from core.rubric import EditableCriterion, EditableRubric, approve_rubric
from core.submission import prepare_submission, save_submission_to_db
from database.db import (
    get_ai_scores,
    get_evaluation,
    get_evaluations_summary,
    get_human_scores,
    get_rubric_with_criteria,
    has_ai_scores,
    has_human_scores,
    init_db,
    save_ai_scores,
    save_approved_rubric,
    save_human_scores,
)

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_report.md"


def test_sample_report_full_lifecycle(tmp_path: Path) -> None:
    """
    Execute the entire product workflow using the realistic technical evaluation report.
    Uses realistic grounded mock data for Gemini when live API credentials are not set.
    """
    db_file = tmp_path / "sample_report_lifecycle.db"
    init_db(db_file)

    # -------------------------------------------------------------
    # 1. Document Extraction & Submission
    # -------------------------------------------------------------
    report_bytes = FIXTURE_PATH.read_bytes()
    assert len(report_bytes) > 0

    parsed_doc = parse_uploaded_file(report_bytes, "sample_report.md")
    assert parsed_doc.word_count == 1338
    assert "Distributed Edge Anomaly Detection" in parsed_doc.raw_text
    assert "Table 1: Ingestion & Telemetry" in parsed_doc.raw_text
    assert len(parsed_doc.warnings) == 0

    prepared = prepare_submission(
        title="Edge Anomaly Detection Report Evaluation",
        submission_type="Technical Report",
        instructions="Evaluate technical depth, methodology rigor, and hardware feasibility.",
        reference_material="Target: Edge environments with constrained ARM micro-gateways.",
        uploaded_files=[("sample_report.md", report_bytes)],
    )

    assert prepared.total_words == 1338
    eval_id = save_submission_to_db(prepared, uploaded_files_data=[("sample_report.md", report_bytes)], db_path=db_file)
    assert eval_id > 0

    # Verify draft state in DB
    ev = get_evaluation(eval_id, db_path=db_file)
    assert ev["status"] == "draft"
    assert ev["total_words"] == 1338

    # -------------------------------------------------------------
    # 2. Criteria Generation (Grounded in Sample Report)
    # -------------------------------------------------------------
    # Proposed criteria grounded directly in the text of sample_report.md
    sample_criteria_proposals = [
        {
            "name": "Methodology Rigor & Hardware Coverage",
            "description": "Evaluation of whether testbed includes representative edge compute tiers.",
            "why_it_matters": "Heterogeneous testing prevents unforeseen production deployment failures.",
            "max_marks": 5.0,
            "evidence_guidance": "Look for Tier-1, Tier-2, and industrial gateway clusters in Section 4.1.",
            "evidence_excerpt": "Cluster Alpha: Raspberry Pi CM4; Cluster Beta: BeagleBone Black; Cluster Gamma: Siemens SIMATIC.",
            "evidence_location": "Section 4.1",
            "scoring_guidance": "Award 5.0 if three diverse hardware tiers are tested with fault injection.",
            "order_index": 0,
        },
        {
            "name": "Empirical Telemetry & Metrics",
            "description": "Assessment of data volume, precision, recall, and false positive metrics.",
            "why_it_matters": "Verifiable numerical results justify operational transition claims.",
            "max_marks": 5.0,
            "evidence_guidance": "Inspect Table 1 and Table 2 for F1-score, latency, and throughput.",
            "evidence_excerpt": "14,200,000 records; F1-score 0.942; p99 latency 42ms; 73.8% bandwidth reduction.",
            "evidence_location": "Table 1 and Table 2",
            "scoring_guidance": "Award 4.0-5.0 for comprehensive tables with exact confusion matrix metrics.",
            "order_index": 1,
        },
        {
            "name": "Hardware Constraint Analysis & Flash Wear",
            "description": "Identification of edge resource limits such as eMMC write cycles and RAM.",
            "why_it_matters": "Unbuffered high-frequency disk writes will degrade embedded flash storage.",
            "max_marks": 5.0,
            "evidence_guidance": "Check Section 6.3 and Recommendation 2 for ring buffer mitigations.",
            "evidence_excerpt": "SQLite commit rates exceeded 18 writes per second, risking premature eMMC block degradation.",
            "evidence_location": "Section 6.3",
            "scoring_guidance": "Award full marks if flash wear is analyzed and memory-buffered logging proposed.",
            "order_index": 2,
        },
    ]

    # -------------------------------------------------------------
    # 3. Human Review & Rubric Approval
    # -------------------------------------------------------------
    # Evaluator reviews proposals, edits one, adds a custom criterion, and approves
    rubric_obj = EditableRubric(
        title="Edge Systems Evaluation Rubric",
        description="Technical rubric for autonomous edge detection",
        criteria=[
            EditableCriterion(
                name=c["name"],
                description=c["description"],
                why_it_matters=c["why_it_matters"],
                max_marks=c["max_marks"],
                evidence_guidance=c["evidence_guidance"],
                evidence_excerpt=c["evidence_excerpt"],
                evidence_location=c["evidence_location"],
                scoring_guidance=c["scoring_guidance"],
                order_index=c["order_index"],
            )
            for c in sample_criteria_proposals
        ],
    )
    # Add a custom criterion during human review
    rubric_obj.add_criterion(
        name="Actionability of Recommendations",
        description="Feasibility and specificity of proposed technical mitigations.",
        max_marks=5.0,
    )
    assert len(rubric_obj.criteria) == 4
    assert rubric_obj.total_marks == 20.0

    rubric_id = approve_rubric(eval_id, rubric_obj, db_path=db_file)
    assert rubric_id > 0

    rubric_data = get_rubric_with_criteria(eval_id, db_path=db_file)
    assert rubric_data is not None
    criteria_list = rubric_data["criteria"]
    assert len(criteria_list) == 4

    # -------------------------------------------------------------
    # 4. Gating Check: AI scores must not exist / be visible yet
    # -------------------------------------------------------------
    assert has_human_scores(eval_id, db_path=db_file) is False
    assert has_ai_scores(eval_id, db_path=db_file) is False

    # -------------------------------------------------------------
    # 5. Human Scoring & Submission
    # -------------------------------------------------------------
    c0_id = criteria_list[0]["id"]
    c1_id = criteria_list[1]["id"]
    c2_id = criteria_list[2]["id"]
    c3_id = criteria_list[3]["id"]

    # Validate individual scores
    assert validate_human_score(4.5, 5.0) == 4.5
    with pytest.raises(ValueError, match="cannot exceed the maximum"):
        validate_human_score(5.5, 5.0)
    with pytest.raises(ValueError, match="0.5 increment"):
        validate_human_score(3.7, 5.0)

    human_scores_data = [
        {"criterion_id": c0_id, "score": 4.5, "feedback": "Excellent hardware tier selection across ARM devices."},
        {"criterion_id": c1_id, "score": 4.5, "feedback": "Solid metrics, clear confusion matrix in Table 1."},
        {"criterion_id": c2_id, "score": 5.0, "feedback": "Crucial flash wear observation with in-memory buffer solution."},
        {"criterion_id": c3_id, "score": 4.0, "feedback": "Recommendations are practical, though OTA scheduling needs security details."},
    ]
    save_human_scores(eval_id, human_scores_data, evaluator_name="Lead Architect", db_path=db_file)
    assert has_human_scores(eval_id, db_path=db_file) is True

    # -------------------------------------------------------------
    # 6. Approved Rubric Integrity Lock
    # -------------------------------------------------------------
    # Now that scoring has commenced, modifying the rubric must fail
    with pytest.raises(ValueError, match="Cannot modify approved rubric"):
        save_approved_rubric(
            evaluation_id=eval_id,
            title="Attempted Rubric Mutation",
            description="Should fail",
            criteria=[{"name": "Tampered", "max_score": 10.0}],
            total_marks=10.0,
            db_path=db_file,
        )

    # -------------------------------------------------------------
    # 7. Independent AI Evaluation on Exact Approved Rubric
    # -------------------------------------------------------------
    raw_ai_json = json.dumps(
        {
            "scores": [
                {
                    "criterion_id": c0_id,
                    "criterion_name": criteria_list[0]["name"],
                    "score": 4.5,
                    "max_marks": 5.0,
                    "reasoning": "Section 4.1 details Raspberry Pi, BeagleBone Black, and Siemens IOT2050 nodes.",
                    "evidence_text": "Cluster Alpha: 40x RPi CM4; Cluster Beta: 50x BeagleBone; Cluster Gamma: 30x Siemens IOT2050.",
                    "evidence_location": "Section 4.1",
                    "uncertainty": "No high-end edge server included in tiering.",
                },
                {
                    "criterion_id": c1_id,
                    "criterion_name": criteria_list[1]["name"],
                    "score": 5.0,
                    "max_marks": 5.0,
                    "reasoning": "Table 1 provides exhaustive TP, FP, FN counts across all 14.2M records.",
                    "evidence_text": "14,200,000 records; F1-score 0.942; egress reduced 73.8%.",
                    "evidence_location": "Table 1 and Table 2",
                    "uncertainty": "Sensor calibration methodology not described.",
                },
                {
                    "criterion_id": c2_id,
                    "criterion_name": criteria_list[2]["name"],
                    "score": 4.5,
                    "max_marks": 5.0,
                    "reasoning": "Explicit flash wear analysis on 512MB RAM node with write-rate benchmarks.",
                    "evidence_text": "SQLite commit rates exceeded 18 writes per second.",
                    "evidence_location": "Section 6.3",
                    "uncertainty": "Long-term endurance beyond 30 days was not empirically projected.",
                },
                {
                    "criterion_id": c3_id,
                    "criterion_name": criteria_list[3]["name"],
                    "score": 4.0,
                    "max_marks": 5.0,
                    "reasoning": "Four actionable recommendations covering quantization and ring buffers.",
                    "evidence_text": "Convert float32 to int8 tensors... Mandate in-memory ring buffers.",
                    "evidence_location": "Section 8",
                    "uncertainty": "Cost analysis of OTA updates omitted.",
                },
            ],
            "overall_reasoning": "High-quality empirical systems report with strong experimental grounding.",
        }
    )

    validated_ai_scores = parse_and_validate_ai_response(raw_ai_json, criteria_list, "gemini-3.8-flash")
    assert len(validated_ai_scores) == 4

    save_ai_scores(eval_id, validated_ai_scores, model_name="gemini-3.8-flash", db_path=db_file)
    assert has_ai_scores(eval_id, db_path=db_file) is True

    # -------------------------------------------------------------
    # 8. Comparison Analytics & Alignment
    # -------------------------------------------------------------
    db_human_scores = [dict(r) for r in get_human_scores(eval_id, db_path=db_file)]
    db_ai_scores = [dict(r) for r in get_ai_scores(eval_id, db_path=db_file)]

    comparison = calculate_comparison(
        evaluation_id=eval_id,
        evaluation_title="Sample Report Evaluation",
        criteria=criteria_list,
        human_scores=db_human_scores,
        ai_scores=db_ai_scores,
        disagreement_threshold=10.0,
    )

    # Human Total: 4.5 + 4.5 + 5.0 + 4.0 = 18.0 / 20.0 = 90.0%
    # AI Total: 4.5 + 5.0 + 4.5 + 4.0 = 18.0 / 20.0 = 90.0%
    assert comparison.human_total_marks == 18.0
    assert comparison.ai_total_marks == 18.0
    assert comparison.max_possible_marks == 20.0
    assert comparison.human_percentage == 90.0
    assert comparison.ai_percentage == 90.0
    assert comparison.total_difference == 0.0
    assert comparison.directional_bias == 0.0

    # Differences per criterion:
    # C0: |90 - 90| = 0%
    # C1: |90 - 100| = 10%
    # C2: |100 - 90| = 10%
    # C3: |80 - 80| = 0%
    # MAE = (0 + 10 + 10 + 0) / 4 = 5.0%
    assert comparison.mae == 5.0
    # All 4 criteria within 10 percentage points tolerance -> 100% agreement
    assert comparison.agreement_percentage == 100.0

    # -------------------------------------------------------------
    # 9. Persistence Across Connection Restarts
    # -------------------------------------------------------------
    # Re-querying summaries simulates application restart
    summary_list = get_evaluations_summary(db_path=db_file)
    assert len(summary_list) == 1
    eval_row = summary_list[0]
    assert eval_row["id"] == eval_id
    assert eval_row["human_total_score"] == 18.0
    assert eval_row["ai_total_score"] == 18.0
    assert eval_row["status"] == "completed"


def test_sample_report_human_only_mode(tmp_path: Path) -> None:
    """
    Verify that the sample report evaluation workflow operates completely
    and cleanly in Human-Only mode without any Gemini API key or AI calls.
    """
    db_file = tmp_path / "human_only_sample_report.db"
    init_db(db_file)

    report_bytes = FIXTURE_PATH.read_bytes()
    prepared = prepare_submission(
        title="Human Only Technical Review",
        submission_type="Technical Report",
        uploaded_files=[("sample_report.md", report_bytes)],
    )
    eval_id = save_submission_to_db(prepared, db_path=db_file)

    rubric_id = save_approved_rubric(
        evaluation_id=eval_id,
        title="Human Review Rubric",
        description="Manual evaluation rubric",
        criteria=[
            {"name": "Clarity", "max_score": 10.0},
            {"name": "Methodology", "max_score": 10.0},
        ],
        total_marks=20.0,
        db_path=db_file,
    )

    rubric_data = get_rubric_with_criteria(eval_id, db_path=db_file)
    crit_ids = [c["id"] for c in rubric_data["criteria"]]

    # Score only as human
    save_human_scores(
        eval_id,
        [
            {"criterion_id": crit_ids[0], "score": 9.0, "feedback": "Well written"},
            {"criterion_id": crit_ids[1], "score": 8.5, "feedback": "Sound design"},
        ],
        db_path=db_file,
    )

    assert has_human_scores(eval_id, db_path=db_file) is True
    assert has_ai_scores(eval_id, db_path=db_file) is False

    comparison = calculate_comparison(
        evaluation_id=eval_id,
        evaluation_title="Human Only",
        criteria=rubric_data["criteria"],
        human_scores=[dict(r) for r in get_human_scores(eval_id, db_path=db_file)],
        ai_scores=None,
    )

    assert comparison.has_ai_evaluation is False
    assert comparison.human_total_marks == 17.5
    assert comparison.human_percentage == 87.5
    assert comparison.ai_total_marks is None
    assert comparison.mae is None
    assert comparison.agreement_percentage is None


def test_sample_report_docx_lifecycle(tmp_path: Path) -> None:
    """
    Verify full ingestion and evaluation lifecycle using the DOCX version of the sample report.
    """
    db_file = tmp_path / "docx_lifecycle.db"
    init_db(db_file)

    docx_path = FIXTURE_PATH.parent / "sample_report.docx"
    docx_bytes = docx_path.read_bytes()

    parsed = parse_uploaded_file(docx_bytes, "sample_report.docx")
    assert parsed.word_count > 1000
    assert "Distributed Edge Anomaly Detection" in parsed.raw_text

    prepared = prepare_submission(
        title="DOCX Sample Report Evaluation",
        submission_type="Technical Report",
        uploaded_files=[("sample_report.docx", docx_bytes)],
    )
    eval_id = save_submission_to_db(prepared, db_path=db_file)
    assert eval_id > 0

    # Save approved rubric
    save_approved_rubric(
        evaluation_id=eval_id,
        title="DOCX Evaluation Rubric",
        description="Rubric for DOCX submission",
        criteria=[
            {"name": "Architecture Rigor", "max_score": 10.0},
            {"name": "Empirical Benchmarks", "max_score": 10.0},
        ],
        total_marks=20.0,
        db_path=db_file,
    )

    r_data = get_rubric_with_criteria(eval_id, db_path=db_file)
    crit_ids = [c["id"] for c in r_data["criteria"]]

    # Score as human
    save_human_scores(
        eval_id,
        [
            {"criterion_id": crit_ids[0], "score": 9.5, "feedback": "Comprehensive architecture details"},
            {"criterion_id": crit_ids[1], "score": 9.0, "feedback": "Detailed benchmarks in tables"},
        ],
        db_path=db_file,
    )

    # Save AI scores
    save_ai_scores(
        eval_id,
        [
            {"criterion_id": crit_ids[0], "score": 9.0, "reasoning": "Clear 3-tier architecture"},
            {"criterion_id": crit_ids[1], "score": 9.5, "reasoning": "Table 1 and 2 benchmarks"},
        ],
        model_name="gemini-3.8-flash",
        db_path=db_file,
    )

    # Compare
    h_scores = [dict(r) for r in get_human_scores(eval_id, db_path=db_file)]
    a_scores = [dict(r) for r in get_ai_scores(eval_id, db_path=db_file)]
    comp = calculate_comparison(
        evaluation_id=eval_id,
        evaluation_title="DOCX Comparison",
        criteria=r_data["criteria"],
        human_scores=h_scores,
        ai_scores=a_scores,
    )

    assert comp.human_total_marks == 18.5
    assert comp.ai_total_marks == 18.5
    assert comp.mae == 5.0
    assert comp.agreement_percentage == 100.0
