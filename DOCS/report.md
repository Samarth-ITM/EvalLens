# EvalLens Project Report

**Product Title:** Human and AI Evaluation Comparison Tool  
**Category:** AI Evaluation  
**Current Status:** Distributable & Independently Verified Release (v1.0.0) — Packaged in `FINAL_BUILD/`, Docker Verified, & Render Ready  
**Maintained by:** Implementation Agent (Antigravity)  
**Product Owner & System Architect:** User  

---

## 1. Product Overview

EvalLens is an AI evaluation comparison tool designed to help evaluators and organizations assess submitted work consistently, rigorously, and transparently.

The workflow begins by accepting submissions (documents, source code, or pasted text) across 15 supported formats (TXT, MD, PDF, DOCX, PY, CPP, H, HPP, JAVA, JS, TS, JSON, HTML, CSS, SQL). Google Gemini AI analyzes the work to propose structured, evidence-grounded criteria. The human evaluator reviews, refines, reorders, and explicitly approves the rubric before any evaluation occurs. Once the rubric is approved:
1. **Independent Human Scoring:** The evaluator scores each criterion with optional qualitative feedback.
2. **Independence Guardrail:** AI scores, recommendations, and explanations remain strictly hidden from the evaluator until human scoring is finalized and submitted (enforced at both UI and backend query levels).
3. **Optional Independent AI Scoring:** Gemini scores the original submission against the exact approved rubric criteria, providing justifications, cited evidence, and uncertainty notes without hallucinating criteria or facts.
4. **Missing Evidence vs Real Zero:** If the submission provides no evidence for a criterion, AI assigns `score: null` (with descriptive explanation), and the criterion is omitted from MAE and agreement rate calculations rather than being penalized as an artificial zero score.
5. **Strict Score Validation:** AI scores exceeding maximum marks, negative scores, or invalid increments are strictly rejected (no silent clamping).
6. **Approved Rubric Integrity:** Once human or AI scoring has commenced, the approved rubric criteria cannot be silently modified or overwritten.
7. **Comparison Analytics & Dashboard:** The application computes normalized score differences, Mean Absolute Error (MAE), agreement percentages within a 10-percentage-point tolerance, signed directional bias, and Pearson correlation (with zero-variance safety), displaying side-by-side alignment in a clean Plotly chart and criterion-level drill-down table.
8. **Five-Tester Prototype Workspace:** Access is protected by a lightweight passkey gate (`evallens2026`). All 5 testers share a common workspace with SQLite WAL concurrency and 5,000ms busy timeout, preventing database locking under concurrent use.

### Core Principle
**AI assists the evaluation process; the human controls the final evaluation.** Human scores represent the authoritative evaluation; AI suggestions serve solely to support consistency and highlight potential oversights.

---

## 2. Current Development Phase

- **Active Phase:** Five-Person Prototype Readiness & Multi-User Verification
- **Phase Goal:** Prepare the existing application for testing by exactly five trusted human evaluators. Guarantee end-to-end workflow reliability, SQLite concurrency (WAL mode & busy timeout), lightweight access protection, transparent missing evidence handling, UI step progress indicators, deployment configuration (`0.0.0.0` and `$PORT`), and multi-user simulation testing.
- **Phase Status:** 100% Complete and Accepted (157 pytest tests passing in 1.06s; full Playwright headed browser suite passed with 0 console errors; 5-user concurrent stress simulation passed with zero database lock errors; `TEST/prototype_acceptance_report.md` generated).

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
| Independence Guardrail (AI scores strictly hidden before human submission) | Series 3 & 4 | Implemented | Tested and passed (UI & backend) |
| Independent AI Scoring on Exact Approved Rubric | Series 3 | Implemented | Tested and passed |
| AI Score Rejection (Strict validation: no silent clamping, 0.5 increments) | Series 4 | Implemented | Tested and passed |
| AI Evidence & Uncertainty Grounding | Series 3 | Implemented | Tested and passed |
| Comparison Analytics (Raw diff, Normalized diff, MAE, Agreement %) | Series 3 | Implemented | Tested and passed |
| Directional Bias & Zero-Variance Correlation Handling | Series 4 | Implemented | Tested and passed |
| Missing AI Score Handling (Excluded from MAE, never treated as zero) | Series 3 | Implemented | Tested and passed |
| Human-Only Workflow (Complete scoring and review without Gemini) | Series 3 | Implemented | Tested and passed |
| Comparison Dashboard (Plotly bar chart + criterion drill-down table) | Series 3 | Implemented | Tested and passed |
| Disagreement Highlighting (> 10 percentage points difference) | Series 3 | Implemented | Tested and passed |
| Separate SQLite Score Persistence (`human_scores` & `ai_scores`) | Series 3 | Implemented | Tested and passed |
| Approved Rubric Integrity (Locked against mutation once scoring begins) | Series 4 | Implemented | Tested and passed |
| Multi-Upload Duplicate Filename Disambiguation | Series 4 | Implemented | Tested and passed |
| Path Traversal Protection (`../../` stripped, uploads boundary validated) | Series 4 | Implemented | Tested and passed |
| Prompt Injection Isolation (`<SUBMISSION_CONTENT>` boundary in prompts) | Series 4 | Implemented | Tested and passed |
| API Transient Retry (Max 2 retries with backoff on 429/503/timeouts) | Series 4 | Implemented | Tested and passed |
| Zero API Key Disclosure (Automatic scrubbing in error messages & logs) | Series 4 | Implemented | Tested and passed |
| Database Integrity (FK enforcement, atomic transaction rollback) | Series 4 | Implemented | Tested and passed |
| Comprehensive Edge Case & Reliability Suite (118 tests) | Series 4 | Implemented | Tested and passed |
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

## 13. Series 4 Reliability Audit & Findings

### 13.1 Critical Scoring Validation (No Clamping)
- **Defect Identified:** Previously in Series 3, `core/evaluator.py` clamped exceeding AI scores to the criterion maximum (`if final_score > max_allowed: final_score = max_allowed`).
- **Correction Applied:** Replaced clamping with strict validation rejection. The function `parse_and_validate_ai_response` now validates that every score is a finite float, non-negative, does not exceed `max_score`, conforms to permitted `0.5` step increments, belongs to an approved criterion in the rubric, contains no duplicates, and leaves no criteria un-evaluated. Violations immediately raise `ValueError` and are rejected from persistence.

### 13.2 Evaluation Independence Verification
- **UI and Backend Enforcement:** The independence guardrail was audited across UI presentation layers and backend database query layers.
- In `database/db.py`, `has_human_scores` must return `True` before `get_ai_scores` is invoked in the comparison dashboard.
- Verified that AI evaluation execution uses `ON CONFLICT` targeting only `ai_scores`, strictly preventing any modification or overwriting of `human_scores`.
- Human evaluators can complete the entire workflow (from rubric review to scoring and history viewing) without configuring a Gemini API key.

### 13.3 Approved Rubric Integrity
- **Mutation Lock:** Once human or AI scoring has commenced for an evaluation (`has_human_scores` or `has_ai_scores`), `save_approved_rubric` raises `ValueError`, refusing to mutate the rubric or alter criteria IDs.
- **Historical Score Association:** Scores in `human_scores` and `ai_scores` remain permanently linked to their original `criterion_id` via SQLite foreign keys.
- **Re-evaluation Workflow:** Evaluators wishing to evaluate work with an edited rubric create a new evaluation session, keeping historical evaluations and scores intact.

### 13.4 Submission Edge Cases & Input Resilience
- **Boundary Verification:** 5,000 words passes; 5,001 words is rejected with detected word count.
- **Corrupted / Blank Documents:** Empty files (0 bytes) parse gracefully with 0 words; corrupted PDFs or DOCXs generate clear extraction warnings without unhandled exceptions; blank/image-only PDFs generate a scanned PDF warning.
- **Unsupported Formats & Size Limits:** Extensions outside the 13 supported formats (.zip, .exe, .png) and files exceeding 10 MB are rejected with explicit errors.
- **Multi-File Uploads:** Duplicate filenames in multiple uploads (e.g. two `main.py` files) are disambiguated as `main.py`, `main_2.py`.
- **Unicode Support:** Tested and verified on emojis, accents, and CJK text. Long lines (15,000+ characters) parse without buffer issues.

### 13.5 Gemini API Resilience & Security
- **Transient Retries:** `execute_with_transient_retry` implements exponential backoff (base delay 0.5s) up to 2 retries for transient errors: rate limits (429), server errors (500, 502, 503, 504), network timeouts, and connection resets.
- **Immediate Failure on Non-Transient Errors:** 400 (Bad Request), 401 (Invalid Key), 403 (Permission Denied), and schema validation failures fail immediately without useless retries.
- **Zero API Key Leakage:** `sanitize_error_message` scrubs API keys (`AIzaSy...`) in all exception strings and replaces them with `[PROTECTED_API_KEY]`. Masked keys in the UI show only the first 4 and last 4 characters.

### 13.6 Security & Abuse Resistance
- **Path Traversal Protection:** Uploaded filenames are sanitized with `sanitize_filename` (stripping directory traversal dots `..`, separators `/` and `\`, and special characters), and verified against `is_relative_to(UPLOADS_DIR)`.
- **SQL Injection Immunity:** All database operations strictly use parameterized queries (`?` placeholders). Payloads like `'; DROP TABLE evaluations; --` and `' OR '1'='1` are safely stored as literal strings.
- **Prompt Injection Isolation:** Both criteria generation and AI scoring prompts isolate untrusted user submission text inside `<SUBMISSION_CONTENT>` XML boundaries with explicit system instructions to ignore prompt overrides, adversarial commands, or requests for full marks.

### 13.7 Comparison Mathematics
- **Formula Verification:** Verified exact mathematical precision of normalized scores, MAE, and agreement percentage.
- **Signed Directional Bias:** Calculated as `human_total - ai_total` (positive when human > AI; negative when AI > human).
- **Pearson Correlation Zero-Variance Safety:** Added `calculate_pearson_correlation` with graceful handling when score variance is zero (returns `None` without division-by-zero crashes).

---

## 14. Actual Test Results

- **Automated Pytest Suite:** 152 tests collected & executed
- **Automated Tests Passed:** 152 (100% pass rate in 0.91s)
- **Headed Browser Test Suite:** Full end-to-end user journey executed in Google Chrome via Playwright (`TEST/integration/test_headed_browser.py`)
- **Browser Console Errors:** 0
- **Browser Page Errors:** 0
- **Milestone Screenshots Captured:** 7 in `TEST/screenshots/`
- **Supported Formats Verified:** All 15 formats verified with live UI upload & extraction
- **Live Gemini Model:** `gemini-3.5-flash-lite` verified for criteria generation (4.34s) and AI scoring (3.35s)

### Test Breakdown by Module:
1. `TEST/unit/test_all_supported_formats.py`: 29 passed (Individual verification of all 15 formats + encrypted PDF)
2. `TEST/unit/test_submission_edge_cases.py`: 14 passed (Empty files, corrupt docs, 5,000/5,001 words, >10MB, Unicode)
3. `TEST/unit/test_gemini_reliability.py`: 11 passed (429/503 retries, 401/403 failure, key scrubbing, empty/malformed responses)
4. `TEST/unit/test_evaluator.py`: 11 passed (Strict score validation, 0.5 increments, independence rule)
5. `TEST/unit/test_document_parser.py`: 12 passed (TXT, MD, PDF, DOCX, code inspection, word limits)
6. `TEST/unit/test_config.py`: 7 passed (Settings, path resolution, default model `gemini-3.5-flash-lite`)
7. `TEST/unit/test_comparison_math.py`: 7 passed (Perfect agreement, polar disagreement, signed bias, unequal weights, zero variance)
8. `TEST/unit/test_security.py`: 6 passed (Path traversal, shell characters, SQLi, XSS, prompt injection)
9. `TEST/unit/test_criteria_generator.py`: 6 passed (V1, V2, V3 prompts, JSON cleaning, grounding)
10. `TEST/unit/test_comparison.py`: 5 passed (MAE, tolerance threshold, missing AI score handling)
11. `TEST/unit/test_database_reliability.py`: 5 passed (FK constraints, atomic rollback, restart persistence, large payloads)
12. `TEST/unit/test_ai_client.py`: 5 passed (BYOK lifecycle, masking, key scrubbing)
13. `TEST/unit/test_validators.py`: 4 passed (Pydantic schema validation)
14. `TEST/unit/test_defects_series6.py`: 2 passed (CriteriaProposalResponse imports, legacy column migration)
15. `TEST/unit/test_rubric.py`: 2 passed (Rubric editing, reordering, total marks)
16. `TEST/integration/test_imports.py`: 12 passed (All core, UI, and config modules import cleanly)
17. `TEST/integration/test_sample_report_workflow.py`: 3 passed (Full lifecycle, human-only mode, DOCX lifecycle on sample report)
18. `TEST/integration/test_database.py`: 4 passed (Database initialization, schema separation)
19. `TEST/integration/test_rubric_integrity.py`: 3 passed (Approved rubric lock after scoring, historical isolation)
20. `TEST/integration/test_submission_and_rubric_db.py`: 2 passed (Multi-document aggregation, rubric approval)
21. `TEST/integration/test_evaluation_flow.py`: 2 passed (Full evaluation lifecycle, human-only workflow)
22. `TEST/integration/test_headed_browser.py`: Complete headed browser automation in Google Chrome

---

## 15. Known Limitations & Operational Recommendations

1. **OCR Exclusion:** Scanned PDFs without extractable text cannot be evaluated (informative warning displayed).
2. **BYOK Session Model:** In-memory API keys are scoped to the user session; restarting the server requires re-entering the key unless provided via environment variables (`GEMINI_API_KEY` / `GOOGLE_API_KEY`).
3. **Recommended Default Model:** Use `gemini-3.5-flash-lite` for high throughput, lowest operational expense (\$0.30/1M in, \$2.50/1M out), and low roundtrip latency (~3.3s). For highly nuanced, multi-step philosophical essays, `gemini-3.8-flash` may optionally be selected in Settings.
4. **Disagreement Threshold:** Configured to a strict 10.0 percentage point tolerance. Criteria exceeding this threshold are flagged with warning badges for manual inspection.

---

## 16. Open Decisions

| Item | Context | Impact | Status |
|---|---|---|---|
| Disagreement Threshold Level | Currently set to 10.0 percentage points as specified in Section 4. | Evaluators can inspect any criterion exceeding 10 pp difference. | Confirmed per specification. |
| Re-scoring / Re-evaluation Policy | Evaluators can edit their scores and re-run AI evaluations if desired. | Previous evaluations are updated in-place per session. | Operational across all series. |

---

## 17. Master Project Checklist

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
- [x] User can paste text or upload files across all 15 supported formats.
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

### Series 4: Testing and Reliability
- [x] Critical scoring validation: AI scores exceeding max, negative, or invalid increments rejected (no silent clamping).
- [x] Independence rule verified at UI and backend query levels (AI scores hidden before human submission; AI cannot overwrite human scores; human-only workflow supported).
- [x] Approved rubric integrity enforced: approved rubrics cannot be silently modified once scoring starts; historical scores preserved.
- [x] Comprehensive submission testing (empty text/files, corrupt PDF/DOCX, unsupported extensions, duplicate filenames, 5,000/5,001 words, >10MB, Unicode).
- [x] Gemini API reliability (transient retries with exponential backoff on 429/503/timeouts; immediate failure on 400/401; zero key exposure).
- [x] Database reliability (missing file init, foreign key constraints, atomic rollback on error, persistence across restarts).
- [x] Security and abuse checks (path traversal sanitization, SQL injection immunity, XSS preservation as safe text, prompt injection isolation).
- [x] Comparison mathematics (MAE correctness, Pearson correlation zero-variance protection, signed directional bias, exact percentages).

### Series 5: Prototype Stabilization, Testing and Final Verification
- [x] Comprehensive audit of existing codebase and elimination of all identified defects.
- [x] Realistic 1,338-word technical report fixture created (`TEST/fixtures/sample_report.md` & `.docx`).
- [x] Individual verification of all 15 supported formats (TXT, MD, PDF, DOCX, PY, CPP, H, HPP, JAVA, JS, TS, JSON, HTML, CSS, SQL).
- [x] Full end-to-end evaluation lifecycle executed with sample report.
- [x] Human-only evaluation mode verified without Gemini API key.
- [x] Gating rules preserved: rubric approval mandatory, AI scoring optional, scores hidden before human submission.
- [x] Automated test suite expanded to 150 tests (100% pass rate in 1.00s).
- [x] Comprehensive test report generated at `TEST/sample_test_report.md`.
- [x] UI stabilized and verified locally on port 8507 (`HTTP 200 OK`).
- [x] Final project report (`DOCS/report.md`) updated.
- [x] Final append-only journal entry added to `DOCS/journal.md`.

### Series 6: Production Verification, Live Gemini Integration, and Headed Browser Testing
- [x] Live Gemini API key verified in project environment without exposure or leakage.
- [x] Cheapest working Gemini text model identified and verified (`gemini-3.5-flash-lite`, \$0.30/1M in, \$2.50/1M out).
- [x] `config/settings.py` updated to set `gemini-3.5-flash-lite` as the default model.
- [x] Headed Google Chrome browser automated using Playwright (`headless=False`) on macOS.
- [x] 0 unhandled console errors and 0 page errors recorded during browser testing.
- [x] All 15 supported formats verified through the live UI (acceptance, text extraction, word counts).
- [x] Realistic 1,338-word technical report evaluated through complete live workflow.
- [x] Grounded criteria generated with verbatim document quotes and citations.
- [x] Human rubric editing and reordering exercised to confirm human control.
- [x] Strict independence rule enforced (AI scores hidden until human submission complete).
- [x] Independent AI scoring completed with live Gemini.
- [x] Comparison dashboard verified (grouped bar chart, MAE, agreement rate, directional bias).
- [x] Evaluation history and persistence verified across browser reload and server restart.
- [x] 7 milestone screenshots captured in `TEST/screenshots/`.
- [x] 4 discovered defects fixed with automated regression tests.
- [x] 152 automated pytest tests passing (100% pass rate in 0.91s).
- [x] Production verification report generated at `TEST/production_verification_report.md`.

### Series 7: Five-Person Prototype Readiness & Multi-User Verification
- [x] Lightweight shared passkey gate implemented (`EVALLENS_ACCESS_PASSWORD`, default `evallens2026`).
- [x] Shared prototype workspace notice prominently displayed (clarifying lack of individual data isolation).
- [x] Session lock / sign out action provided in sidebar navigation.
- [x] SQLite WAL (Write-Ahead Logging) mode and 5,000ms busy timeout enabled on all database connections.
- [x] Schema updated for nullable `ai_scores.score REAL` to handle missing evidence without forcing zero scores.
- [x] Automatic database migration implemented in `_migrate_columns_if_missing()` for legacy databases.
- [x] Missing evidence excluded from MAE and agreement rate denominator.
- [x] UI usability enhanced with visual step progress breadcrumb indicators across setup, review, evaluation, and comparison.
- [x] Submission extraction summary card expanded by default (`expanded=True`) on the Review step.
- [x] Deployment configuration created (`.streamlit/config.toml` binding to `0.0.0.0`, port 8501, `$PORT` support).
- [x] Multi-user simulation test suite created (`test_five_user_simulation.py`) verifying sequential and concurrent access.
- [x] Multi-threaded SQLite concurrency stress test passed (5 simultaneous worker threads, 0 lock errors).
- [x] Full automated test suite expanded to 157 tests (100% pass rate in 1.06s).
- [x] Headed browser test re-verified with live access password gate and persistence across reload.
- [x] Comprehensive acceptance report generated at `TEST/prototype_acceptance_report.md`.

### Series 8: Final Build, Independent Verification, Docker Packaging and Deployment
- [x] Completely separate distributable folder created (`FINAL_BUILD/`).
- [x] Development cruft excluded (0 tests, 0 journals, 0 reports, 0 screenshots, 0 git, 0 venv, 0 databases).
- [x] Runtime dependencies isolated in `FINAL_BUILD/requirements.txt` (lean production requirements).
- [x] Hardened Docker container (`FINAL_BUILD/Dockerfile`) using `python:3.12-slim` and non-root `evallens` user.
- [x] Multi-container orchestration defined in `FINAL_BUILD/docker-compose.yml` with persistent volume mounts.
- [x] Render deployment blueprint created (`FINAL_BUILD/render.yaml`) with persistent disk attachment.
- [x] Distributable zip archive created (`FINAL_BUILD.zip`, 60 KB).
- [x] Comprehensive deployment and user documentation written (`FINAL_BUILD/README.md`).
- [x] Hosted environment security guard implemented (safe failure if `EVALLENS_ACCESS_PASSWORD` missing in prod).
- [x] Dynamic uploads directory resolved from `settings.uploads_dir` across container volumes.
- [x] Docker image built (`final_build-evallens:latest`) and container executed locally.
- [x] Playwright Chrome browser automated against live Docker container (`http://localhost:8501`).
- [x] Container restart and volume persistence verified (evaluation records survived container restart).
- [x] Architectural incompatibility analysis completed for Vercel (Render selected as official host).
- [x] Automated test suite expanded to 159 tests (100% pass rate in 24.99s).
- [x] Final build verification report generated at `TEST/final_build_verification_report.md`.

### Series 9: Final GitHub Push, Render Deployment and Release Verification
- [x] Existing private GitHub repository configured: `https://github.com/Samarth-ITM/EvalLens.git`.
- [x] Branches `main` and `master` pushed to GitHub with complete commit history (commit `8dddfb3a0567a8881f4ddce993df68c635ef9370`).
- [x] All secrets (`.env`), SQLite databases (`data/evallens.db`), and user uploads (`uploads/*`) strictly excluded from Git.
- [x] Render service provisioned via Render CLI: `evallens` (ID `srv-dbjm3p8u01pc73fskbng`).
- [x] Live web service built and deployed at `https://evallens.onrender.com`.
- [x] Health check verified: `https://evallens.onrender.com/_stcore/health` returns `HTTP/2 200 OK`.
- [x] Automated end-to-end browser verification executed against live Render service (`TEST/integration/test_render_live_deployment_e2e.py`).
- [x] Live end-to-end workflow verified with real DOCX document (`sample_report.docx`):
  - Passkey gate authentication with `evallens2026`.
  - Document upload and automatic text extraction.
  - Live Gemini criteria generation (`gemini-3.5-flash-lite`).
  - Rubric review and human approval.
  - Human scoring submission.
  - Independent AI scoring on approved criteria.
  - Comparison dashboard rendering (metrics, bias, charts, agreement).
  - Evaluation history persistence verification.
- [x] Visual evidence captured: 10 screenshots in `DOCS/screenshots/render_live/`.
- [x] Vercel incompatibility documented and verified (stateless lambdas vs stateful Streamlit WebSockets/SQLite).
- [x] 0 critical or major defects remaining.

---

## 9. Five-Person Prototype Usage Instructions

EvalLens is configured as a private evaluation prototype for five trusted human testers.

### Tester Credentials & Access
- **Access URL:** `http://localhost:8501` (or your private hosted URL)
- **Shared Access Password:** `evallens2026` (configurable via `EVALLENS_ACCESS_PASSWORD` in `.env`)
- **Shared Workspace Notice:** All evaluations, submitted documents, and rubrics are visible across all 5 testers. Please do not submit proprietary, classified, or sensitive personally identifiable information (PII).

### Standard Evaluation Journey
1. **Login:** Enter the shared prototype password `evallens2026` and click **Access Workspace**.
2. **Setup Submission (`New Evaluation`):**
   - Provide an Evaluation Title (e.g. *CS101 Final Project Review*).
   - Select the Submission Type (*Written Work*, *Code*, *Software Project*, *Technical Report*, *Custom*).
   - Upload one or more files (TXT, MD, PDF, DOCX, PY, CPP, H, HPP, JAVA, JS, TS, JSON, HTML, CSS, SQL) or paste text directly. Total submission must not exceed 5,000 words.
   - Click **Analyze Submission with Gemini** (or **Create Rubric Manually** if evaluating without AI).
3. **Review & Refine Rubric:**
   - Review the proposed criteria, descriptions, and evidence citations.
   - Edit criteria names, descriptions, or maximum marks as needed.
   - Click **Approve Rubric & Save Evaluation**.
4. **Human Evaluation (`Evaluate`):**
   - Score each criterion between 0.0 and the criterion maximum using 0.5 increments.
   - Enter optional feedback or qualitative notes.
   - Click **Submit Human Evaluation** (or **Save Progress** as draft).
   - *Independence Notice:* AI suggestions remain strictly locked and invisible until you click Submit.
5. **Independent AI Evaluation:**
   - Once human evaluation is submitted, click **Run AI Evaluation with Gemini**.
   - Gemini evaluates the submission against the approved criteria in approximately 3 to 8 seconds.
6. **Inspect Comparison Dashboard:**
   - View side-by-side Plotly bar chart comparing Human vs. AI scores per criterion.
   - Inspect summary metrics: Human Total, AI Suggestion, Directional Bias (pts), MAE (%), and Agreement Rate (%).
   - Expand criterion alignment cards to read AI reasoning, quoted evidence excerpts, and uncertainty notes.
7. **Review Past Sessions (`Evaluation History`):**
   - View past evaluations, access rubrics, and inspect comparison states at any time.

---

## 10. Deployment and Recovery Instructions

### Local Execution
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Verify dependencies
pip install -r requirements.txt

# 3. Ensure .env contains your configuration
# GEMINI_API_KEY=your_key_here
# EVALLENS_ACCESS_PASSWORD=evallens2026

# 4. Launch Streamlit
streamlit run app.py
```

### Hosting on Render (Web Service)
1. **Repository:** Connect the EvalLens Git repository to Render.
2. **Environment:** Select **Python 3**.
3. **Build Command:**
   ```bash
   pip install --upgrade pip && pip install -r requirements.txt
   ```
4. **Start Command:**
   ```bash
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
5. **Environment Variables on Render:**
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `EVALLENS_ACCESS_PASSWORD`: Set your private 5-person passkey (e.g. `evallens2026`).
   - `DB_PATH`: `/var/data/evallens.db` (if using Render Persistent Disks).
   - `UPLOADS_PATH`: `/var/data/uploads` (if using Render Persistent Disks).
6. **Persistent Disk (Recommended on Render):**
   - Mount a Render Persistent Disk at `/var/data` (size: 1 GB is ample for 5 testers).
   - This ensures SQLite database records and uploaded files survive service restarts and deploys.
7. **Disaster Recovery:**
   - SQLite backups can be performed while running using the SQLite online backup API or simply copying the DB file while WAL mode handles active transactions:
     ```bash
     sqlite3 /var/data/evallens.db ".backup /var/data/evallens_backup.db"
     ```

---

## 11. Known Limitations, Risks, and Remaining Bugs

1. **Shared Workspace Nature (No User Isolation):** All 5 testers operate within a single shared database. There is no multi-tenant isolation or personal user account dashboard. Testers can view and edit each other's evaluations.
2. **Disk Persistence on Ephemeral Platforms:** If deployed on Render or Heroku without a persistent disk mount, the local SQLite database and uploads directory reset to default upon service redeploy. Mount a persistent disk at `/var/data` as documented above.
3. **Scanned / Image-Only PDFs:** The prototype parses textual PDF streams (`pypdf`). Image-only scanned PDFs return an informative warning advising the user to paste text or provide a digital document. OCR is explicitly out of scope for this prototype.
4. **Internet Dependency for AI Inference:** Criteria generation and AI evaluation require an outbound connection to `generativelanguage.googleapis.com`. Human scoring and comparison viewing functions completely offline without internet.
5. **No Absolute Ground Truth:** The tool measures alignment and divergence between human evaluators and AI rubric suggestions; it does not claim to establish an absolute objective truth.
