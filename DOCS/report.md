# EvalLens Project Report

**Product Title:** Human and AI Evaluation Comparison Tool  
**Category:** AI Evaluation  
**Current Status:** Series 2 Complete (Series 2 of 5)  
**Maintained by:** Implementation Agent (Antigravity)  
**Product Owner & System Architect:** User  

---

## 1. Product Overview

EvalLens is an AI evaluation comparison tool designed to help evaluators and organizations assess submitted work consistently, rigorously, and transparently.

The workflow begins by accepting submissions (documents, source code, or pasted text) across 13 formats. Google Gemini AI analyzes the work to propose structured, evidence-grounded criteria. The human evaluator reviews, refines, reorders, and explicitly approves the rubric before any evaluation occurs. Independent scoring (both human and AI) and alignment comparisons follow in subsequent series.

### Core Principle
**AI assists the evaluation process; the human controls the final evaluation.** The user retains authority over rubric approval and final grading.

---

## 2. Current Development Phase

- **Active Series:** Series 2 of 5 (Submission and AI Criteria Generation)
- **Phase Goal:** Implement document extraction for 13 supported formats, enforce strict 5,000-word submission limit and 10 MB file limits, build Gemini criteria generation with 3 prompt strategies and evidence grounding, create interactive rubric editing and explicit approval, and store separate AI proposals and approved rubrics in SQLite.
- **Series 2 Status:** Complete and verified.

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
| Verbatim Quotation Grounding and Line/Page Citation | Series 2 | Implemented | Tested and passed |
| Human Rubric Review Interface (Edit, Add, Delete, Reorder) | Series 2 | Implemented | Tested and passed |
| Dynamic Total Marks Calculation (Default: 5 marks/criterion) | Series 2 | Implemented | Tested and passed |
| Explicit Rubric Approval & Database Persistence | Series 2 | Implemented | Tested and passed |
| Distinguishable AI Proposals vs. Human-Approved Rubrics in SQLite | Series 2 | Implemented | Tested and passed |
| Human-Only Workflow (Manual Rubric Creation without API Key) | Series 2 | Implemented | Tested and passed |
| Automated Test Suite (53 unit & integration tests) | Series 1 & 2 | Implemented | Tested and passed |
| Human Scoring & AI Scoring Execution | Series 3 | Not implemented | Not tested |
| Comparison Analytics & Dashboard | Series 3 | Not implemented | Not tested |
| Comprehensive Edge Case & Reliability Suite | Series 4 | Not implemented | Not tested |
| Exporting & Multi-Platform Packaging | Series 5 | Not implemented | Not tested |

---

## 4. Architecture and Technology Stack

- **Language:** Python 3.12 (compatible with Python 3.11+)
- **UI Framework:** Streamlit
- **AI Integration:** Google GenAI Python SDK (`google-genai>=2.30.0`), targeting models `gemini-3.8-flash`, `gemini-3.5-flash-lite`, and `gemini-4-argon`
- **Document Processing:** `pypdf>=5.0.0` for PDF page and text extraction; `python-docx>=1.1.0` for Word documents; native UTF-8/Latin-1 text decoders with line numbering
- **Database:** SQLite (`sqlite3` standard library) with foreign keys and migrations
- **Data Validation:** Pydantic v2 (`pydantic>=2.7.0`)
- **Testing:** `pytest>=8.0.0`
- **Environment Management:** `python-dotenv`

---

## 5. Repository Structure

```
EvalLens/
├── app.py                      # Main Streamlit application and view routing
├── requirements.txt            # Python dependencies (updated with pypdf and python-docx)
├── README.md                   # User guide, setup instructions, and Series 2 workflow
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
│   ├── evaluator.py            # [Placeholder] Evaluation orchestration (Series 3)
│   ├── comparison.py           # [Placeholder] Alignment & score comparison (Series 3)
│   └── validators.py           # Pydantic validation schemas (criteria, submissions, keys)
│
├── database/
│   ├── db.py                   # SQLite connection manager, parameterized queries, migrations
│   └── schema.sql              # Normalized database schema with separate AI proposal & approved rubrics
│
├── ui/
│   ├── pages/
│   │   ├── home.py             # Home overview & recent evaluations listing
│   │   ├── new_evaluation.py   # Multi-step submission, AI criteria generation, rubric editor
│   │   ├── history.py          # Database-backed history with approved rubrics & criteria
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
│   │   └── test_rubric.py              # Rubric editing, total marks, reordering
│   ├── integration/
│   │   ├── test_database.py                    # SQLite init, tables, foreign keys
│   │   ├── test_imports.py                     # Clean imports of all modules
│   │   └── test_submission_and_rubric_db.py    # End-to-end submission, AI proposals, rubric approval
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

## 6. Files Created and Modified

### Created in Series 2
- `TEST/unit/test_document_parser.py`
- `TEST/unit/test_criteria_generator.py`
- `TEST/unit/test_rubric.py`
- `TEST/integration/test_submission_and_rubric_db.py`

### Modified in Series 2
- `requirements.txt` (Added `pypdf>=5.0.0` and `python-docx>=1.1.0`)
- `database/schema.sql` (Added `ai_criteria_proposals` table and columns for submission metadata, prompt versions, and approved rubric tracking)
- `database/db.py` (Added automated schema migration runner, CRUD operations for evaluations, submissions, AI proposals, and approved rubrics)
- `core/validators.py` (Added `CriterionProposal`, `CriteriaProposalResponse`, deduplication logic, and `EvaluationCreate` fields)
- `core/document_parser.py` (Implemented multi-format parsing for 13 extensions, line/page tracking, 5,000-word limit, and 10 MB check)
- `core/submission.py` (Implemented aggregation, disk persistence to `uploads/`, and database saving)
- `core/criteria_generator.py` (Implemented prompts V1, V2, V3, structured JSON parsing, evidence grounding, and error sanitization)
- `core/rubric.py` (Implemented `EditableCriterion`, `EditableRubric`, reordering, total mark sum, and approval persistence)
- `ui/pages/new_evaluation.py` (Replaced placeholder with full 3-step interactive evaluation setup, review, editing, and approval UI)
- `ui/pages/history.py` (Updated to display approved rubrics, criteria details, and submission counts)
- `ui/pages/home.py` (Updated to show recent evaluations with submission type and word counts)
- `README.md` (Updated status to Series 2, added step-by-step workflow guide)
- `DOCS/report.md` (Updated with Series 2 implementations, tests, and roadmap)
- `DOCS/journal.md` (Appended Series 2 entry)

---

## 7. Database Design

The SQLite database enforces strict relational integrity with foreign keys and cascade deletes:

1. **`evaluations`**: Evaluation sessions (`id`, `title`, `description`, `submission_type`, `instructions`, `reference_material`, `status`, `prompt_version`, `total_words`, `created_at`, `updated_at`).
2. **`submissions`**: Uploaded or pasted content linked to an evaluation (`id`, `evaluation_id`, `title`, `content`, `file_name`, `file_path`, `file_type`, `word_count`, `warnings`, `created_at`).
3. **`ai_criteria_proposals`**: Pristine, immutable AI criteria suggestions (`id`, `evaluation_id`, `name`, `description`, `why_it_matters`, `max_marks`, `evidence_guidance`, `evidence_excerpt`, `evidence_location`, `scoring_guidance`, `prompt_version`, `order_index`, `created_at`).
4. **`rubrics`**: Approved or active evaluation rubrics (`id`, `evaluation_id`, `title`, `description`, `status`, `total_marks`, `is_approved`, `approved_at`, `prompt_version`, `created_at`, `updated_at`).
5. **`rubric_criteria`**: Human-approved, edited, or manually created criteria (`id`, `rubric_id`, `name`, `description`, `why_it_matters`, `max_score`, `weight`, `evidence_guidance`, `evidence_excerpt`, `evidence_location`, `scoring_guidance`, `is_ai_generated`, `order_index`, `created_at`).
6. **`human_scores` & `ai_scores`**: Distinct score tables (reserved for Series 3).

### Key Architectural Safeguard
The initial AI proposal is archived in `ai_criteria_proposals`, while the human-edited and approved criteria reside in `rubrics` and `rubric_criteria`. This keeps the AI proposal and the approved rubric distinguishable for future auditability and comparison.

---

## 8. BYOK Implementation and Security Approach

- In-memory session retention (`st.session_state`) ensures API keys are never persisted to SQLite or written to disk.
- Keys are masked in the UI (`AIza••••••••xxxx`).
- All exceptions are intercepted by `sanitize_error_message` to prevent key exposure in logs or UI error banners.
- When no API key is available, the human-only workflow enables full evaluation creation and manual rubric building without failure.

---

## 9. Installation Instructions

```bash
# 1. Activate virtual environment
source .venv/bin/activate       # macOS / Linux
# or .venv\Scripts\Activate.ps1 # Windows PowerShell

# 2. Install dependencies (including pypdf and python-docx)
pip install -r requirements.txt
```

---

## 10. Commands to Run the Application

```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 11. Tests Executed and Actual Results

All tests executed via `.venv/bin/pytest -v`.

### Test Summary
- **Total Tests Collected:** 53
- **Passed:** 53
- **Failed:** 0
- **Errors:** 0
- **Duration:** 2.20 seconds

### Detailed Results by Suite
1. **`TEST/unit/test_document_parser.py` (8 tests):**
   - `test_txt_and_md_extraction`: PASSED
   - `test_pdf_extraction_with_page_markers`: PASSED
   - `test_scanned_pdf_warning`: PASSED
   - `test_docx_extraction`: PASSED
   - `test_code_file_extraction_supported_languages`: PASSED (11 code languages verified)
   - `test_unsupported_file_formats_rejected`: PASSED (ZIP, PPTX, PNG, JPG, EXE rejected)
   - `test_file_size_limit_enforced`: PASSED (> 10 MB rejected)
   - `test_word_counting_and_5000_limit`: PASSED (5,000 words allowed, 5,001 rejected)
2. **`TEST/unit/test_criteria_generator.py` (8 tests):**
   - `test_prompt_versions_building`: PASSED (V1, V2, V3 prompt structure verified)
   - `test_clean_json_text`: PASSED (fenced JSON blocks parsed)
   - `test_criteria_schema_validation_and_deduplication`: PASSED (case-insensitive deduplication)
   - `test_criteria_schema_rejects_empty_list`: PASSED
   - `test_missing_key_raises_value_error`: PASSED
   - `test_empty_submission_raises_value_error`: PASSED
   - `test_mocked_gemini_generation_success`: PASSED (mocked Gemini structured output)
   - `test_mocked_gemini_invalid_json`: PASSED
3. **`TEST/unit/test_rubric.py` (2 tests):**
   - `test_rubric_creation_and_total_marks`: PASSED
   - `test_rubric_editing_and_reordering`: PASSED (add, edit, move up, move down, delete)
4. **`TEST/integration/test_submission_and_rubric_db.py` (2 tests):**
   - `test_submission_and_rubric_persistence_lifecycle`: PASSED (multi-file submission persisted)
   - `test_db_rubric_approval_isolation`: PASSED (AI proposal vs approved rubric isolation verified)
5. **Series 1 Regression Tests (33 tests):**
   - `test_database.py` (4 tests): PASSED
   - `test_imports.py` (16 tests): PASSED
   - `test_ai_client.py` (5 tests): PASSED
   - `test_config.py` (4 tests): PASSED
   - `test_validators.py` (4 tests): PASSED

---

## 12. Known Limitations

1. **Scanned PDFs:** Optical Character Recognition (OCR) is intentionally excluded in this prototype. Scanned PDFs yield an informative warning.
2. **Pure Code Inspection:** Code files are evaluated as structured text; code execution or unit test runners are not implemented.
3. **Session-Scoped BYOK:** Terminating the server process requires re-entering the Gemini key unless loaded from `.env`.

---

## 13. Open Decisions

| Item | Context | Impact | Status |
|---|---|---|---|
| Criteria Scale Granularity | Currently criteria default to 5.0 marks with 0.5 increments. | Scoring interface in Series 3 will use this scale. | Open for confirmation by Product Owner. |
| Automatic Word Count Trimming vs User Reduction | Current behavior strictly rejects submissions > 5,000 words. | Complies with instruction: "Do not silently truncate content." | Closed / Confirmed per spec. |

---

## 14. Remaining Tasks (Roadmap to Series 3)

- [ ] Implement human scoring interface in `ui/pages/` and `core/evaluator.py`.
- [ ] Implement optional AI scoring runner using Gemini with approved criteria.
- [ ] Build alignment and score comparison calculations in `core/comparison.py`.
- [ ] Build comparison dashboard with Plotly visual cards.
- [ ] Connect human and AI score persistence into SQLite `human_scores` and `ai_scores` tables.

---

## 15. Master Project Checklist

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
- [x] User can select submission type (Written Work, Code, Software Project, Technical Report, Custom).
- [x] User can add optional evaluation instructions.
- [x] User can add optional reference material (kept separate from submitted work).
- [x] User can paste submission text.
- [x] User can upload supported files (TXT, MD, PDF, DOCX, PY, CPP, H, HPP, JAVA, JS, TS, JSON, HTML, CSS, SQL).
- [x] Multiple file uploads supported.
- [x] TXT and MD extraction with line numbers.
- [x] PDF extraction with page markers.
- [x] DOCX extraction with paragraphs and tables.
- [x] Code file inspection as text.
- [x] Combined submission limit of 5,000 words enforced.
- [x] Oversized submissions rejected with detected word count.
- [x] Gemini criteria generation using BYOK client.
- [x] Three prompt versions maintained (V1, V2, V3 default).
- [x] Evidence grounding with verbatim excerpts and line/page citations.
- [x] Criteria can be edited, added, removed, and reordered.
- [x] Maximum marks configurable (default 5.0).
- [x] Total marks calculate dynamically.
- [x] Human can explicitly approve the rubric.
- [x] Approved rubric and AI proposals persist distinguishably in SQLite.
- [x] Existing Series 1 tests pass (33/33).
- [x] New Series 2 tests pass (20/20).
- [x] DOCS/report.md updated.
- [x] DOCS/journal.md received new appended entry.

### Series 3: Human and AI Evaluation (Pending)
- [ ] Human scoring.
- [ ] Optional AI scoring.
- [ ] Score comparison.
- [ ] Dashboard.
- [ ] Evaluation history.

### Series 4: Testing and Reliability (Pending)
- [ ] Unit and integration tests.
- [ ] Edge cases.
- [ ] API failure handling.
- [ ] Validation.
- [ ] Security and reliability checks.

### Series 5: Product Completion and Portability (Pending)
- [ ] Interface refinement.
- [ ] Exporting.
- [ ] Documentation.
- [ ] Installation on another laptop.
- [ ] Demonstration.
- [ ] Final acceptance testing.
