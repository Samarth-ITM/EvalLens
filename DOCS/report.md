# EvalLens Project Report

**Product Title:** Human and AI Evaluation Comparison Tool  
**Category:** AI Evaluation  
**Current Status:** Series 3 Complete (Series 3 of 5)  
**Maintained by:** Implementation Agent (Antigravity)  
**Product Owner & System Architect:** User  

---

## 1. Product Overview

EvalLens is an AI evaluation comparison tool designed to help evaluators and organizations assess submitted work consistently, rigorously, and transparently.

The workflow begins by accepting submissions (documents, source code, or pasted text) across 13 formats. Google Gemini AI analyzes the work to propose structured, evidence-grounded criteria. The human evaluator reviews, refines, reorders, and explicitly approves the rubric before any evaluation occurs. Once the rubric is approved:
1. **Independent Human Scoring:** The evaluator scores each criterion with optional qualitative feedback.
2. **Independence Guardrail:** AI scores, recommendations, and explanations remain strictly hidden from the evaluator until human scoring is finalized and submitted.
3. **Optional Independent AI Scoring:** Gemini scores the original submission against the exact approved rubric criteria, providing justifications, cited evidence, and uncertainty notes without hallucinating criteria or facts.
4. **Comparison Analytics & Dashboard:** The application computes normalized score differences, Mean Absolute Error (MAE), and agreement percentages within a 10-percentage-point tolerance, displaying side-by-side alignment in a clean Plotly chart and criterion-level drill-down table.

### Core Principle
**AI assists the evaluation process; the human controls the final evaluation.** Human scores represent the authoritative evaluation; AI suggestions serve solely to support consistency and highlight potential oversights.

---

## 2. Current Development Phase

- **Active Series:** Series 3 of 5 (Human Evaluation, AI Evaluation and Comparison)
- **Phase Goal:** Implement the human scoring interface with validated bounds and 0.5 decimal increments, build the independent AI scoring engine using Gemini on approved rubrics, enforce the independence rule (hiding AI scores until human submission), calculate normalized comparison metrics (MAE and 10 pp agreement rate), create a Plotly-backed comparison dashboard, and persist scores separately in SQLite.
- **Series 3 Status:** Complete and verified.

---

## 3. Implemented Features

| Feature / Capability | Phase | Status | Verification State |
|---|---|---|---|
| Repository Architecture & Structure | Series 1 | Implemented | Tested and passed |
| Path Management & Portable Configuration (`pathlib`) | Series 1 | Implemented | Tested and passed |
| SQLite Initialization & Automatic Schema Setup | Series 1 | Implemented | Tested and passed |
| Distinct Schema for Human vs. AI Scores | Series 1 | Implemented | Tested and passed |
| BYOK (Bring Your Own Key) Gemini Manager | Series 1 | Implemented | Tested and passed |
| In-Memory Session Storage (Zero disk/DB persistence) | Series 1 | Implemented | Tested and passed |
| Document Extraction (TXT, MD, PDF, DOCX) | Series 2 | Implemented | Tested and passed |
| Code File Inspection (PY, CPP, H, HPP, JAVA, JS, TS, JSON, HTML, CSS, SQL) | Series 2 | Implemented | Tested and passed |
| 5,000-Word Total Submission Limit Enforcement | Series 2 | Implemented | Tested and passed |
| 10 MB Per-File Limit Enforcement | Series 2 | Implemented | Tested and passed |
| Rejection of Unsupported Formats (ZIP, PPTX, image formats, OCR) | Series 2 | Implemented | Tested and passed |
| Separation of Graded Submission vs Reference Material | Series 2 | Implemented | Tested and passed |
| Multi-file + Pasted Text Aggregation | Series 2 | Implemented | Tested and passed |
| Gemini Criteria Generation with Evidence Grounding | Series 2 | Implemented | Tested and passed |
| Three Prompt Strategies (V1 Basic, V2 Instructions, V3 Grounded Default) | Series 2 | Implemented | Tested and passed |
| Human Rubric Review Interface (Edit, Add, Delete, Reorder) | Series 2 | Implemented | Tested and passed |
| Explicit Rubric Approval & Database Persistence | Series 2 | Implemented | Tested and passed |
| Distinguishable AI Proposals vs. Human-Approved Rubrics in SQLite | Series 2 | Implemented | Tested and passed |
| Human Scoring Interface (0.5 increments, 0 to max_marks) | Series 3 | Implemented | Tested and passed |
| Human Score Validation & Bound Enforcement | Series 3 | Implemented | Tested and passed |
| Progress Saving (Draft) & Final Submission Actions | Series 3 | Implemented | Tested and passed |
| Independence Guardrail (AI scores strictly hidden before human submission) | Series 3 | Implemented | Tested and passed |
| Independent AI Scoring on Exact Approved Rubric | Series 3 | Implemented | Tested and passed |
| AI Score Validation & Clamping to Criterion Maximum | Series 3 | Implemented | Tested and passed |
| AI Evidence & Uncertainty Grounding | Series 3 | Implemented | Tested and passed |
| Comparison Analytics (Raw diff, Normalized diff, MAE, Agreement %) | Series 3 | Implemented | Tested and passed |
| Missing AI Score Handling (Excluded from MAE, never treated as zero) | Series 3 | Implemented | Tested and passed |
| Human-Only Workflow (Complete scoring and review without Gemini) | Series 3 | Implemented | Tested and passed |
| Comparison Dashboard (Plotly bar chart + criterion drill-down table) | Series 3 | Implemented | Tested and passed |
| Disagreement Highlighting (> 10 percentage points difference) | Series 3 | Implemented | Tested and passed |
| Separate SQLite Score Persistence (`human_scores` & `ai_scores`) | Series 3 | Implemented | Tested and passed |
| Comprehensive Edge Case & Reliability Suite | Series 4 | Not implemented | Not tested |
| Exporting & Multi-Platform Packaging | Series 5 | Not implemented | Not tested |

---

## 4. Architecture and Technology Stack

- **Language:** Python 3.12 (compatible with Python 3.11+)
- **UI Framework:** Streamlit
- **Visualizations:** Plotly (`plotly.graph_objects`)
- **AI Integration:** Google GenAI Python SDK (`google-genai>=2.30.0`), targeting models `gemini-3.8-flash`, `gemini-3.5-flash-lite`, and `gemini-4-argon`
- **Document Processing:** `pypdf>=5.0.0` and `python-docx>=1.1.0`
- **Database:** SQLite (`sqlite3` standard library) with foreign keys and migrations
- **Data Validation:** Pydantic v2 (`pydantic>=2.7.0`)
- **Testing:** `pytest>=8.0.0`
- **Environment Management:** `python-dotenv`

---

## 5. Comparison Mathematical Formulas

As required by Section 4:

1. **Normalized Score:**
   $$\text{Normalized Score} = \left(\frac{\text{Score}}{\text{Maximum Marks}}\right) \times 100$$
2. **Normalized Absolute Difference:**
   $$\text{Normalized Difference}_i = |\text{Normalized Human}_i - \text{Normalized AI}_i|$$
3. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{1}{K} \sum_{i=1}^K \text{Normalized Difference}_i$$
   *Where $K$ is the count of evaluated criteria where both human and AI scores exist. Missing AI scores are excluded and never treated as zero.*
4. **Agreement Percentage:**
   $$\text{Agreement Percentage} = \left(\frac{\text{Count of criteria where } \text{Normalized Difference}_i \le 10.0}{K}\right) \times 100$$
5. **Significant Disagreement:**
   $$\text{Flagged if } \text{Normalized Difference}_i > 10.0 \text{ percentage points}$$

*Note:* Human scores are not described as "ground truth", nor does MAE measure "AI accuracy"; metrics represent alignment and inter-rater agreement between independent scoring passes.

---

## 6. Repository Structure

```
EvalLens/
├── app.py                      # Main Streamlit application and view routing (5 tabs)
├── requirements.txt            # Python dependencies
├── README.md                   # User guide, setup instructions, and evaluation workflow
├── pytest.ini                  # Pytest configuration (pythonpath, testpaths)
├── .env.example                # Example environment variables (no secrets)
├── .gitignore                  # Git exclusions for .venv, data, caches, keys
│
├── config/
│   └── settings.py             # Pathlib-based settings, model definitions, env loading
│
├── core/
│   ├── submission.py           # Submission validation, word counting, disk and DB persistence
│   ├── document_parser.py      # Multi-format text extraction, line/page markers, limits
│   ├── ai_client.py            # Gemini BYOK client manager, masking, live connection test
│   ├── criteria_generator.py   # Prompts (V1, V2, V3), Gemini calling, evidence grounding
│   ├── rubric.py               # EditableRubric models, reordering, total marks, approval
│   ├── evaluator.py            # Human score submission, AI scoring execution, independence checks
│   ├── comparison.py           # Comparison metrics: normalized diff, MAE, agreement rate
│   └── validators.py           # Pydantic validation schemas (scoring, criteria, submissions, keys)
│
├── database/
│   ├── db.py                   # SQLite connection manager, parameterized queries, migrations
│   └── schema.sql              # Normalized database schema with separate AI proposal & score tables
│
├── ui/
│   ├── pages/
│   │   ├── home.py             # Home overview & recent evaluations with score badges
│   │   ├── new_evaluation.py   # Multi-step submission, AI criteria generation, rubric editor
│   │   ├── evaluate.py         # Human scoring, independent AI scoring, comparison dashboard
│   │   ├── history.py          # Database-backed history with approved rubrics, criteria & scores
│   │   └── settings_page.py    # BYOK Gemini setup, connection test, model selector
│   ├── components/
│   │   └── header.py           # Shared product header
│   └── styles/
│       └── main.css            # Professional styling rules
│
├── DOCS/
│   ├── report.md               # Maintained project report
│   └── journal.md              # Append-only development journal
│
├── TEST/
│   ├── unit/
│   │   ├── test_ai_client.py           # BYOK handling, masking, sanitization
│   │   ├── test_config.py              # Settings, path resolution, security repr
│   │   ├── test_validators.py          # Pydantic models & validation rules
│   │   ├── test_document_parser.py     # Extraction across 13 formats, word limits, size checks
│   │   ├── test_criteria_generator.py  # Prompt generation, schema validation, mocked AI, dedup
│   │   ├── test_rubric.py              # Rubric editing, total marks, reordering
│   │   ├── test_comparison.py          # Normalized diffs, MAE, agreement rate, missing AI scores
│   │   └── test_evaluator.py           # Human score validation, AI bounds, independence rule
│   ├── integration/
│   │   ├── test_database.py                    # SQLite init, tables, foreign keys
│   │   ├── test_imports.py                     # Clean imports of all modules
│   │   ├── test_submission_and_rubric_db.py    # Multi-file submission, AI proposal vs rubric DB
│   │   └── test_evaluation_flow.py             # Full evaluation lifecycle & human-only workflow
│   ├── fixtures/
│   │   └── sample_data.py              # Temporary database test fixtures
│   └── README.md                       # Test instructions
│
├── data/
│   └── .gitkeep                # Local database storage directory (gitignored)
│
└── uploads/
    └── .gitkeep                # Local upload storage directory (gitignored)
```

---

## 7. Files Created and Modified

### Created in Series 3
- `core/comparison.py` (Implemented comparison calculations: normalized scores, MAE, agreement rate, missing AI handling)
- `ui/pages/evaluate.py` (Implemented scoring interface, independence protection, AI scoring runner, and Plotly dashboard)
- `TEST/unit/test_comparison.py` (Unit tests for comparison mathematics, missing scores, boundary cases)
- `TEST/unit/test_evaluator.py` (Unit tests for human score bounds, AI score clamping, and independence rule)
- `TEST/integration/test_evaluation_flow.py` (Integration tests for full scoring flow and human-only evaluation)

### Modified in Series 3
- `core/evaluator.py` (Implemented human score validation, AI scoring prompt building, AI score validation, and independence enforcement)
- `core/validators.py` (Added `HumanCriterionScoreInput`, `AICriterionScoreResult`, and `AIEvaluationResponse`)
- `database/schema.sql` (Added `evidence_location` and `uncertainty` columns to `ai_scores`)
- `database/db.py` (Added migrations, human score persistence, AI score persistence, and query methods)
- `app.py` (Added `Evaluate` tab to navigation and updated version tag)
- `ui/pages/new_evaluation.py` (Added direct "Score Evaluation ➔" button on approval)
- `ui/pages/history.py` (Added score metrics and direct "Evaluate / Compare ➔" quick actions)
- `ui/pages/home.py` (Added score tags and quick navigation to Evaluate view)
- `TEST/integration/test_imports.py` (Added `ui.pages.evaluate` to import tests)
- `README.md` (Updated status to Series 3, documented full evaluation workflow)
- `DOCS/report.md` (Updated with Series 3 features, mathematical formulas, and test results)
- `DOCS/journal.md` (Appended Series 3 entry)

---

## 8. Database Design

1. **`evaluations`**: Evaluation sessions (`id`, `title`, `description`, `submission_type`, `instructions`, `reference_material`, `status`, `prompt_version`, `total_words`, `created_at`, `updated_at`). Status transitions: `draft` -> `rubric_proposed` -> `rubric_approved` -> `human_evaluated` -> `completed`.
2. **`submissions`**: Uploaded or pasted content linked to an evaluation.
3. **`ai_criteria_proposals`**: Pristine, immutable AI criteria suggestions.
4. **`rubrics`**: Approved evaluation rubrics.
5. **`rubric_criteria`**: Approved criteria linked to rubrics.
6. **`human_scores`**: Human evaluator scores and feedback (`id`, `evaluation_id`, `criterion_id`, `score`, `feedback`, `evaluator_name`, `created_at`, `updated_at`).
7. **`ai_scores`**: AI evaluation scores (`id`, `evaluation_id`, `criterion_id`, `score`, `reasoning`, `evidence_text`, `evidence_location`, `uncertainty`, `model_name`, `created_at`, `updated_at`).

### Independence and Isolation Safeguard
Human and AI scores reside in strictly separate tables. AI evaluation never touches, overwrites, or updates rows in `human_scores`. Human evaluations are never overwritten silently.

---

## 9. BYOK Implementation and Security Approach

- In-memory session retention (`st.session_state`) ensures API keys are never persisted to SQLite or written to disk.
- Keys are masked in the UI (`AIza••••••••xxxx`).
- All exceptions are intercepted by `sanitize_error_message` to prevent key exposure in logs or UI error banners.
- When no API key is available, the human-only workflow enables full evaluation creation, manual rubric building, and human scoring without failure.

---

## 10. Installation Instructions

```bash
# 1. Activate virtual environment
source .venv/bin/activate       # macOS / Linux
# or .venv\Scripts\Activate.ps1 # Windows PowerShell

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 11. Commands to Run the Application

```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 12. Tests Executed and Actual Results

All tests executed via `.venv/bin/pytest -v`.

### Test Summary
- **Total Tests Collected:** 67
- **Passed:** 67
- **Failed:** 0
- **Duration:** 0.73 seconds

### Detailed Results by Suite
1. **`TEST/unit/test_comparison.py` (5 tests):**
   - `test_calculate_normalized_score`: PASSED (normalized score formula)
   - `test_comparison_calculations_full_agreement`: PASSED (100% agreement, MAE=0.0)
   - `test_comparison_calculations_within_and_exceeding_tolerance`: PASSED (MAE, agreement with 10 pp threshold)
   - `test_missing_ai_scores_not_treated_as_zero`: PASSED (missing AI scores excluded from MAE, never treated as 0)
   - `test_human_only_evaluation_handling`: PASSED (clean report without comparison when AI is absent)
2. **`TEST/unit/test_evaluator.py` (6 tests):**
   - `test_validate_human_score_boundaries`: PASSED (bounds `[0, max]`, negatives rejected, decimals accepted)
   - `test_build_ai_scoring_prompt`: PASSED (prompt includes exact approved criteria)
   - `test_parse_and_validate_ai_response_valid`: PASSED (structured AI score validation)
   - `test_parse_ai_response_clamps_exceeding_scores`: PASSED (clamping AI scores to max_score)
   - `test_parse_ai_response_rejects_malformed_json`: PASSED (malformed JSON rejected)
   - `test_independence_rule_ai_scores_hidden_before_human_submission`: PASSED (AI scores hidden before human submit)
3. **`TEST/integration/test_evaluation_flow.py` (2 tests):**
   - `test_full_evaluation_and_comparison_lifecycle`: PASSED (end-to-end rubric approval -> human scoring -> AI scoring -> comparison)
   - `test_human_only_workflow_persistence`: PASSED (human scoring persisted without AI scores)
4. **Series 1 & 2 Regression Tests (54 tests):**
   - `test_database.py` (4 tests): PASSED
   - `test_imports.py` (17 tests, including `evaluate.py`): PASSED
   - `test_submission_and_rubric_db.py` (2 tests): PASSED
   - `test_ai_client.py` (5 tests): PASSED
   - `test_config.py` (4 tests): PASSED
   - `test_criteria_generator.py` (8 tests): PASSED
   - `test_document_parser.py` (8 tests): PASSED
   - `test_rubric.py` (2 tests): PASSED
   - `test_validators.py` (4 tests): PASSED

---

## 13. Known Limitations

1. **OCR Exclusion:** Scanned PDFs without extractable text cannot be evaluated (informative warning displayed).
2. **Deterministic Mocking in Tests:** Automated tests use deterministic mocks to avoid API cost and network flakiness. Live Gemini evaluation operates identically in production via BYOK.
3. **Session-Scoped Key:** API keys are retained in session memory; restarting the server requires re-entering the key unless set in `.env`.

---

## 14. Open Decisions

| Item | Context | Impact | Status |
|---|---|---|---|
| Disagreement Threshold Level | Currently set to 10.0 percentage points as specified in Section 4. | Evaluators can inspect any criterion exceeding 10 pp difference. | Confirmed per specification. |
| Re-scoring / Re-evaluation Policy | Evaluators can edit their scores and re-run AI evaluations if desired. | Previous evaluations are updated in-place per session. | Operational in Series 3. |

---

## 15. Remaining Tasks (Roadmap to Series 4)

- [ ] Comprehensive unit and integration test coverage for edge cases.
- [ ] Network failure and API rate limit resilience checks.
- [ ] Large document stress testing near the 5,000-word limit.
- [ ] Input sanitization, SQL injection resistance, and security auditing.
- [ ] Error boundary hardening so UI never breaks on malformed state.

---

## 16. Master Project Checklist

### Series 1: Foundation, Architecture, and Local Setup
- [x] Repository structure created cleanly and accurately.
- [x] Application skeleton built with Streamlit.
- [x] Local setup runnable via one documented command (`streamlit run app.py`).
- [x] BYOK configuration foundation implemented with strict security.
- [x] SQLite database foundation initialized with separate `human_scores` and `ai_scores` tables.
- [x] Jargon-free interface with honest empty states ("No evaluations yet").
- [x] Maintain project report (`DOCS/report.md`).
- [x] Maintain append-only journal (`DOCS/journal.md`).

### Series 2: Submission and AI Criteria Generation
- [x] User can create an evaluation.
- [x] User can select submission type.
- [x] User can add optional instructions and separate reference material.
- [x] User can paste text or upload files across 13 supported formats.
- [x] Combined submission limit of 5,000 words enforced (no silent truncation).
- [x] Gemini criteria generation with 3 prompt versions (V3 default).
- [x] Evidence grounding with verbatim excerpts and line/page citations.
- [x] Criteria can be edited, added, removed, and reordered.
- [x] Human can explicitly approve the rubric.
- [x] Approved rubric and AI proposals persist distinguishably in SQLite.

### Series 3: Human and AI Evaluation
- [x] Human can evaluate an approved rubric.
- [x] Human can enter scores and comments (0.5 increments, validated bounds).
- [x] Scores are validated against criterion maximums.
- [x] Human can save progress (draft) and submit evaluation.
- [x] AI evaluation is optional.
- [x] AI uses the exact approved rubric criteria (cannot alter criteria).
- [x] AI provides evidence excerpts, citations, and uncertainty explanations.
- [x] AI scores are strictly hidden until human submission is confirmed.
- [x] AI cannot overwrite human scores.
- [x] Human-only workflow works cleanly without Gemini.
- [x] Comparison calculations are correct (Normalized scores, MAE, 10 pp agreement rate).
- [x] Missing AI results handled correctly (excluded from MAE, never treated as zero).
- [x] Comparison dashboard displays both evaluations with Plotly charts.
- [x] Results persist in SQLite (`human_scores`, `ai_scores`).
- [x] Evaluation history displays scores and comparison status.
- [x] Series 1 and Series 2 regression tests pass.
- [x] New Series 3 tests pass (14 new tests, 67 total).
- [x] DOCS/report.md is updated.
- [x] DOCS/journal.md has a new appended entry.

### Series 4: Testing and Reliability (Pending)
- [ ] Unit and integration tests for edge cases.
- [ ] API failure and retry handling.
- [ ] Validation and stress testing.
- [ ] Security and reliability checks.

### Series 5: Product Completion and Portability (Pending)
- [ ] Interface refinement.
- [ ] Exporting.
- [ ] Documentation.
- [ ] Installation on another laptop.
- [ ] Demonstration.
- [ ] Final acceptance testing.
