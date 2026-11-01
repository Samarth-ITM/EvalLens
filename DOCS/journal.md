# EvalLens Development Journal

An append-only record of development sessions, technical decisions, tests, and milestones.

---

## Entry: 2026-11-01 18:38:00 IST — Series 1 Completion

### Date and Time
2026-11-01 18:38:00 IST

### Development Series
Series 1 of 5: Foundation, Architecture, and Local Setup

### Objective
Establish the project foundation, clean repository architecture, SQLite database layer with separate human/AI score tables, Gemini BYOK (Bring Your Own Key) manager with zero-leakage security, Streamlit application skeleton with 4 distinct views, initial test suite in `TEST/`, and comprehensive project documentation.

### Work Completed
1. Inspected initial workspace `/Users/samarth/Downloads/STUFF/WORK/ITM/PE-MiniProject` (found empty) and initialized git repository.
2. Created standard modular directory structure: `config/`, `core/`, `database/`, `ui/pages/`, `ui/components/`, `ui/styles/`, `DOCS/`, `TEST/unit/`, `TEST/integration/`, `TEST/fixtures/`, `data/`, and `uploads/`.
3. Created Python virtual environment with Python 3.12 (`.venv`) and installed dependencies: `streamlit`, `google-genai`, `pydantic`, `plotly`, `pytest`, `python-dotenv`.
4. Formulated configuration management in `config/settings.py` utilizing `pathlib` for cross-platform portability and safe representation that hides sensitive environment values.
5. Designed and created normalized SQLite database schema in `database/schema.sql` separating `human_scores` and `ai_scores` and enforcing foreign key constraints.
6. Implemented SQLite database manager in `database/db.py` with automatic, idempotent schema initialization (`init_db`) and parameterized SQL queries.
7. Developed Pydantic validators in `core/validators.py` for API key validation, evaluation models, and rubric criteria.
8. Implemented BYOK manager in `core/ai_client.py` adhering to all 13 security rules: keys kept in server memory only, masked display (`AIza••••••••xxxx`), live connection test to Gemini API, and exception sanitization to avoid leaking keys.
9. Added future-phase placeholder modules in `core/` (`submission.py`, `document_parser.py`, `criteria_generator.py`, `rubric.py`, `evaluator.py`, `comparison.py`) with clear phase markers.
10. Built clean Streamlit interface with 4 views (Home, New Evaluation, Evaluation History, Settings) adhering to plain-English, non-jargon copy and honest empty states.
11. Created full automated test suite inside `TEST/` covering configuration loading, database initialization, table creation, module imports, and missing key handling.
12. Configured `pytest.ini` with `pythonpath = .` and verified that 33 out of 33 tests pass.
13. Verified Streamlit live server execution (`http://localhost:8501`) returning HTTP 200 OK.
14. Authored `DOCS/report.md` (15 required sections) and initialized `DOCS/journal.md`.

### Files Created
- `.env.example`
- `.gitignore`
- `requirements.txt`
- `pytest.ini`
- `README.md`
- `app.py`
- `config/settings.py`
- `core/validators.py`
- `core/ai_client.py`
- `core/submission.py`
- `core/document_parser.py`
- `core/criteria_generator.py`
- `core/rubric.py`
- `core/evaluator.py`
- `core/comparison.py`
- `database/schema.sql`
- `database/db.py`
- `ui/styles/main.css`
- `ui/components/header.py`
- `ui/pages/home.py`
- `ui/pages/new_evaluation.py`
- `ui/pages/history.py`
- `ui/pages/settings_page.py`
- `TEST/README.md`
- `TEST/fixtures/__init__.py`
- `TEST/fixtures/sample_data.py`
- `TEST/unit/__init__.py`
- `TEST/unit/test_config.py`
- `TEST/unit/test_ai_client.py`
- `TEST/unit/test_validators.py`
- `TEST/integration/__init__.py`
- `TEST/integration/test_database.py`
- `TEST/integration/test_imports.py`
- `data/.gitkeep`
- `uploads/.gitkeep`
- `DOCS/report.md`
- `DOCS/journal.md`

### Files Modified
None (all files created fresh during Series 1 in an initially empty workspace).

### Technical Decisions Explicitly Specified by Product Owner
1. Implement Series 1 only; do not prematurely implement Series 2–5.
2. Technology stack: Python, Streamlit, Google Gemini via official `google-genai` SDK, SQLite, Pydantic, Plotly, pytest, git.
3. Keep application logic strictly separate from the UI.
4. Human and AI scores must be stored in distinct, separate tables.
5. BYOK security: zero hardcoded keys, never store keys in SQLite, DOCS, or logs, hold entered key in session memory only, sanitize exception messages, and test connection with a live Gemini API call.
6. Honest empty states ("No evaluations yet") and plain-English messaging without technical jargon.
7. Maintain two mandatory documentation files: `DOCS/report.md` (15 structured sections) and `DOCS/journal.md` (append-only development history).

### Commands Executed
1. `ls -la` — Inspected workspace.
2. `git status` — Checked git status (uninitialized).
3. `python3 --version && which python3` — Verified local Python 3.14 / 3.12 availability.
4. `uv python list` — Checked installed Python versions.
5. `/Users/samarth/.local/bin/uv venv .venv --python 3.12` — Created Python 3.12 virtual environment.
6. `git init` — Initialized git repository.
7. `mkdir -p config core database ui/pages ui/components ui/styles DOCS TEST/unit TEST/integration TEST/fixtures data uploads` — Created directory hierarchy.
8. `/Users/samarth/.local/bin/uv pip install --python .venv/bin/python streamlit google-genai pydantic plotly pytest python-dotenv` — Installed project dependencies.
9. `.venv/bin/pytest -v` — Ran pytest suite (initially failed collection due to missing `pythonpath`, resolved via `pytest.ini`).
10. `.venv/bin/pytest -v` — Executed full test suite after adding `pytest.ini` (33 passed).
11. `.venv/bin/streamlit run app.py --server.headless true --server.port 8501` — Launched application in background.
12. `curl -I http://localhost:8501/` — Verified HTTP 200 OK response from application.
13. `.venv/bin/python -c "from database.db import init_db, list_tables; init_db(); print('Tables:', list_tables())"` — Verified SQLite database creation and table generation.
14. `git status --ignored` — Verified git tracking and `.gitignore` exclusion of `.venv/`, `data/evallens.db`, and caches.

### Tests Performed
1. Unit tests for configuration and path resolution (`TEST/unit/test_config.py`).
2. Unit tests for BYOK management, key masking, error sanitization, and missing-key handling (`TEST/unit/test_ai_client.py`).
3. Unit tests for Pydantic input validation (`TEST/unit/test_validators.py`).
4. Integration tests for SQLite initialization, idempotency, foreign key integrity, and table existence (`TEST/integration/test_database.py`).
5. Integration tests for all 16 application modules importing cleanly (`TEST/integration/test_imports.py`).
6. Live HTTP response check on running Streamlit server (`curl -I http://localhost:8501/`).

### Actual Test Results
- Pytest suite: 33 tests executed, 33 passed, 0 failed (duration: 0.76s).
- Streamlit application: Started successfully, bound to port 8501, responded with HTTP 200 OK.
- Database: Created `data/evallens.db` with all 6 tables (`ai_scores`, `evaluations`, `human_scores`, `rubric_criteria`, `rubrics`, `submissions`).

### Errors Encountered
- **Error:** When initially running `.venv/bin/pytest -v`, pytest failed collection with `ModuleNotFoundError: No module named 'database'`.
  - **Resolution:** Created `pytest.ini` at project root with `pythonpath = .` and `testpaths = TEST` so that pytest automatically resolves top-level package imports without requiring manual `PYTHONPATH` exports across different operating systems.

### Known Issues
None. The foundation is stable and verified.

### Next Development Tasks
Series 2 (Submission and AI Criteria):
1. Implement submission processing in `core/submission.py` and document text extraction in `core/document_parser.py`.
2. Implement evaluation modes and Gemini rubric criteria generation in `core/criteria_generator.py`.
3. Support citation and evidence references extracted from submitted work.
4. Build editable and approvable rubric review interface in `ui/pages/new_evaluation.py`.



---

## Entry: 2026-11-01 19:00:00 IST — Series 2 Completion

### Date and Time
2026-11-01 19:00:00 IST

### Development Series
Series 2 of 5: Submission and AI Criteria Generation

### Objective
Implement multi-format submission ingestion (13 supported extensions), enforce the 5,000-word submission limit and 10 MB per-file limits, build Gemini AI criteria generation with three prompt versions and evidence grounding, create the human rubric review, editing, reordering, and explicit approval interface, and persist both AI proposals and approved rubrics in SQLite.

### Work Completed
1. Integrated `pypdf` and `python-docx` for document parsing and added them to `requirements.txt`.
2. Implemented `core/document_parser.py`:
   - Text and code extraction for 13 formats (`.txt`, `.md`, `.pdf`, `.docx`, `.py`, `.cpp`, `.h`, `.hpp`, `.java`, `.js`, `.ts`, `.json`, `.html`, `.css`, `.sql`).
   - Line numbering for code and text (`L1: ...`).
   - Page markers for PDF files (`[Page 1]`).
   - Explanatory warning for image-only/scanned PDFs lacking extractable text.
   - Enforced 10 MB maximum file size and strict rejection of unsupported file formats (ZIP, PPTX, images, executables).
   - Word counting across single and multiple files.
   - Strict 5,000-word limit validation rejecting oversized submissions with clear messages.
3. Implemented `core/submission.py`:
   - Aggregated multi-file uploads and pasted text.
   - Enforced distinct separation of contextual reference materials from graded submission text.
   - Sanitized filenames and persisted uploaded files to `uploads/`.
   - Saved submission records and metadata to the SQLite database.
4. Implemented `core/criteria_generator.py`:
   - Built 3 prompt strategies: V1 (basic), V2 (with evaluator instructions and reference materials), and V3 (evidence-grounded with anti-hallucination rules and uncertainty handling, default).
   - Structured JSON response generation using Gemini BYOK client.
   - Cleaned markdown code blocks from model outputs.
   - Grounded evidence extracts linking criteria to verbatim submission text and line/page citations.
   - Built anti-duplication filter and limitation note support.
5. Implemented `core/rubric.py`:
   - Built `EditableCriterion` and `EditableRubric` models.
   - Enabled editing of criterion names, descriptions, max marks, evidence guidance, and scoring guidance.
   - Added custom criteria addition, deletion, and reordering (`move_up`, `move_down`).
   - Dynamic total marks calculation (default: 5.0 marks per criterion).
   - Explicit rubric approval workflow persisting approved rubrics to SQLite and updating evaluation status.
6. Extended SQLite Database (`database/schema.sql`, `database/db.py`):
   - Created `ai_criteria_proposals` table to store pristine AI proposals separately from human-edited rubrics.
   - Added automatic migration helper in `db.py` to upgrade existing databases safely without data loss.
   - Added database CRUD functions for submissions, AI proposals, and approved rubrics.
7. Developed Streamlit UI Views:
   - `ui/pages/new_evaluation.py`: Built 3-step interactive submission form, review & edit cards with reordering/deletion, and confirmation view. Added manual human-only rubric creation mode that operates without requiring an API key.
   - `ui/pages/history.py`: Enhanced to display approved rubrics, criteria breakdowns, evidence excerpts, total marks, and submission metadata.
   - `ui/pages/home.py`: Updated to display recent evaluations with submission types, word counts, and status badges.
8. Authored Unit & Integration Tests in `TEST/`:
   - `TEST/unit/test_document_parser.py` (8 tests)
   - `TEST/unit/test_criteria_generator.py` (8 tests)
   - `TEST/unit/test_rubric.py` (2 tests)
   - `TEST/integration/test_submission_and_rubric_db.py` (2 tests)
   - Verified that all 53 tests (33 from Series 1 + 20 new tests) pass cleanly.
9. Verified application launch on port 8502 returning HTTP 200 OK.
10. Updated `README.md` and `DOCS/report.md`.

### Files Created
- `TEST/unit/test_document_parser.py`
- `TEST/unit/test_criteria_generator.py`
- `TEST/unit/test_rubric.py`
- `TEST/integration/test_submission_and_rubric_db.py`

### Files Modified
- `requirements.txt`
- `database/schema.sql`
- `database/db.py`
- `core/validators.py`
- `core/document_parser.py`
- `core/submission.py`
- `core/criteria_generator.py`
- `core/rubric.py`
- `ui/pages/new_evaluation.py`
- `ui/pages/history.py`
- `ui/pages/home.py`
- `README.md`
- `DOCS/report.md`
- `DOCS/journal.md`

### Technical Decisions Explicitly Specified by Product Owner
1. Supported formats strictly limited to: TXT, MD, PDF, DOCX, PY, CPP, H, HPP, JAVA, JS, TS, JSON, HTML, CSS, SQL.
2. No ZIP, PPTX, image uploads, or OCR.
3. Maximum submission size: 5,000 words total per evaluation. If exceeded, reject the submission, display detected word count, explain limit, and ask user to reduce. Do not silently truncate.
4. Maximum file size: 10 MB per file.
5. Reference material must remain separate from actual submission.
6. Support text, files, or both.
7. Code files inspected strictly as text without claiming execution.
8. Maintain 3 prompt versions (V1, V2, V3 default).
9. Ground evidence in actual extracted content; never invent page numbers, filenames, line numbers, or quotations.
10. Default maximum marks: 5.0 per criterion. Total criteria: approximately 3–8.
11. Rubric must not be considered approved until the human explicitly approves it.
12. Keep AI proposals and approved rubrics distinguishable in SQLite.
13. Human-only workflows must remain usable without a Gemini key.
14. Do not implement scoring or comparison yet (belongs to Series 3).

### Commands Executed
1. `.venv/bin/python -c "...check docx/pdf libraries..."`
2. `/Users/samarth/.local/bin/uv pip install --python .venv/bin/python pypdf python-docx`
3. `.venv/bin/pytest -v` — Ran regression check on Series 1 tests (33 passed).
4. `.venv/bin/pytest -v` — Ran test suite with Series 2 tests (53 passed).
5. `.venv/bin/streamlit run app.py --server.headless true --server.port 8502` — Tested app launch.
6. `curl -I http://localhost:8502/` — Confirmed HTTP 200 OK.

### Tests Performed
1. Multi-format text extraction (TXT, MD, PDF, DOCX).
2. Code extraction across 11 programming/scripting formats.
3. Scanned PDF empty text warning detection.
4. Word counting accuracy and multi-file word count summation.
5. 5,000-word limit boundary tests (4,999 passed, 5,000 passed, 5,001 rejected).
6. 10 MB per-file size limit enforcement.
7. Rejection of forbidden formats (.zip, .pptx, .png, .jpg, .exe).
8. Prompt generation across V1, V2, and V3.
9. JSON cleaning from markdown fences.
10. Pydantic validation of criteria schema and case-insensitive deduplication.
11. Mocked Gemini criteria generation and handling of invalid JSON responses.
12. Safe handling of missing Gemini API keys.
13. Rubric total mark summation, adding, editing, deleting, and reordering criteria.
14. End-to-end multi-file submission persistence.
15. Separate persistence and isolation of AI proposals vs approved rubrics in SQLite.
16. Evaluation status transition to 'rubric_approved'.

### Actual Test Results
- Pytest suite: 53 tests collected, 53 passed, 0 failed in 2.20s.
- Streamlit application: Started successfully on port 8502, returned HTTP 200 OK.

### Errors Encountered
- **Error:** Initial test assertions in `test_txt_and_md_extraction` miscounted expected word counts (9 vs 10 for essay text, 3 vs 4 for markdown header due to markdown symbol tokenization).
  - **Resolution:** Corrected test assertions to match exact token extraction results.

### Known Issues
None. All Series 2 features are implemented and verified.

### Next Development Tasks
Series 3 (Human and AI Evaluation):
1. Implement human scoring interface against approved rubric criteria.
2. Implement optional AI scoring runner using Google Gemini.
3. Calculate alignment, variance, and comparison metrics in `core/comparison.py`.
4. Build the comparison dashboard and score history views.
5. Connect human and AI score persistence in SQLite `human_scores` and `ai_scores` tables.


---

## Entry: 2026-11-01 19:12:00 IST — Series 3 Completion

### Date and Time
2026-11-01 19:12:00 IST

### Development Series
Series 3 of 5: Human Evaluation, AI Evaluation and Comparison

### Objective
Implement the complete evaluation workflow: human scoring with validated 0.5 increments, independent AI evaluation on exact approved rubrics, strict independence enforcement (hiding AI scores until human submission), comparison analytics (normalized scores, MAE, agreement percentage within 10 percentage points), Plotly comparison dashboard, and relational persistence.

### Work Completed
1. Extended SQLite schema and database manager (`database/schema.sql`, `database/db.py`):
   - Added `evidence_location` and `uncertainty` columns to `ai_scores`.
   - Added automatic migration check ensuring existing databases upgrade smoothly without data loss.
   - Implemented persistence methods `save_human_scores`, `get_human_scores`, `save_ai_scores`, `get_ai_scores`, `has_human_scores`, and `has_ai_scores`.
   - Enhanced `get_evaluations_summary` with human and AI total score metrics.
2. Implemented `core/validators.py`:
   - Added validation models `HumanCriterionScoreInput`, `AICriterionScoreResult`, and `AIEvaluationResponse`.
3. Implemented `core/comparison.py`:
   - Formulated normalized score computation: `(score / max_marks) * 100`.
   - Formulated normalized absolute difference: `|human_normalized - ai_normalized|`.
   - Formulated MAE: mean of normalized absolute differences across evaluated criteria.
   - Formulated agreement percentage: percentage of criteria with normalized difference <= 10 percentage points.
   - Guarded missing AI score handling so absent AI scores are never treated as zero.
   - Handled human-only evaluations returning clean summaries without comparison metrics.
4. Implemented `core/evaluator.py`:
   - Validated human score boundaries (`0.0 <= score <= max_marks`) with 0.5 step support.
   - Built prompt for Gemini AI scoring strictly constrained to the approved rubric criteria.
   - Validated AI scores ensuring no score exceeds criterion maximums (clamping if exceeded).
   - Enforced the Independence Rule via `get_visible_ai_scores_for_review`: AI scores remain hidden until human scoring is submitted.
   - Guaranteed AI scoring never modifies or overwrites human scores.
5. Built Streamlit Views:
   - `ui/pages/evaluate.py`: Multi-section evaluation and dashboard workspace (Submission Overview, Human Scoring Form, Optional AI Scoring, Plotly Comparison Bar Chart, and Detailed Criterion Drill-down Table).
   - `app.py`: Added `Evaluate` tab to navigation and updated version tag to v0.3.0.
   - `ui/pages/new_evaluation.py`: Added direct "Score Evaluation ➔" action on rubric approval.
   - `ui/pages/history.py`: Added score metrics and direct "Evaluate / Compare ➔" quick actions.
   - `ui/pages/home.py`: Added score tags and quick navigation to Evaluate view.
6. Authored Automated Tests in `TEST/`:
   - `TEST/unit/test_comparison.py` (5 tests)
   - `TEST/unit/test_evaluator.py` (6 tests)
   - `TEST/integration/test_evaluation_flow.py` (2 tests)
   - Updated `TEST/integration/test_imports.py` to verify `ui.pages.evaluate`.
   - Verified that all 67 tests pass cleanly.
7. Verified live application launch on port 8503 returning HTTP 200 OK.
8. Updated `README.md` and `DOCS/report.md`.

### Files Created
- `core/comparison.py`
- `ui/pages/evaluate.py`
- `TEST/unit/test_comparison.py`
- `TEST/unit/test_evaluator.py`
- `TEST/integration/test_evaluation_flow.py`

### Files Modified
- `core/evaluator.py`
- `core/validators.py`
- `database/schema.sql`
- `database/db.py`
- `app.py`
- `ui/pages/new_evaluation.py`
- `ui/pages/history.py`
- `ui/pages/home.py`
- `TEST/integration/test_imports.py`
- `README.md`
- `DOCS/report.md`
- `DOCS/journal.md`

### Technical Decisions Explicitly Specified by Product Owner
1. Score input uses 0.5 increments by default and must be between 0 and criterion maximum marks.
2. AI evaluation is strictly optional and uses the existing Gemini BYOK client.
3. AI must evaluate using the exact human-approved rubric and cannot create new criteria or alter the rubric.
4. AI must not invent evidence; report limitations clearly.
5. Critical Independence Rule: Human must submit evaluation before AI scores become visible. AI results remain hidden until human submission is complete.
6. AI must never overwrite human scores.
7. Comparison formulas:
   - Normalized score = `(score / maximum marks) * 100`
   - Normalized absolute difference = `|human_normalized - ai_normalized|`
   - MAE = average of normalized absolute differences across evaluated criteria
   - Agreement percentage = percentage of criteria whose normalized difference is <= 10 percentage points
8. Handle missing AI scores correctly without treating them as zero.
9. Do not describe human scores as ground truth or claim MAE measures AI accuracy.
10. Dashboard labels: "Human score", "AI suggestion", "Difference". Never present AI score as final result.
11. Support human-only evaluation without requiring a Gemini key.

### Commands Executed
1. `pytest -v` — Ran full test suite (67 tests collected, initially 1 failure due to foreign key test setup in isolated test db, resolved).
2. `pytest -v` — Executed full test suite after resolution (67 passed in 0.73s).
3. `streamlit run app.py --server.headless true --server.port 8503` — Tested application launch.
4. `curl -I http://localhost:8503/` — Confirmed HTTP 200 OK.

### Tests Performed
1. Human score boundary checks (`[0, max]`, negatives rejected, decimals accepted).
2. AI prompt generation ensuring exact approved criteria are specified.
3. AI score parsing and validation against criterion maximums.
4. AI score clamping when model returns scores exceeding rubric limits.
5. Malformed AI response rejection.
6. Independence Rule enforcement (AI scores hidden before human submission, unhidden after).
7. Normalized score calculation.
8. MAE calculation across multiple criteria.
9. Agreement percentage calculation within 10 percentage points tolerance.
10. Missing AI score handling (excluded from MAE, never treated as 0).
11. Human-only evaluation handling without comparison.
12. Full evaluation lifecycle integration test (rubric approval -> human scoring -> AI scoring -> comparison).
13. Human-only workflow integration test with database persistence.
14. Regression tests for Series 1 and Series 2.

### Actual Test Results
- Pytest suite: 67 tests collected, 67 passed, 0 failed in 0.73s.
- Streamlit application: Started successfully on port 8503, returned HTTP 200 OK.

### Errors Encountered
- **Error:** In `test_independence_rule_ai_scores_hidden_before_human_submission`, `eval_id=99` was used without inserting parent evaluation or criterion rows first, causing SQLite `FOREIGN KEY constraint failed`.
  - **Resolution:** Updated test to create the evaluation and criterion records in the test database prior to testing score insertion and visibility checks.

### Known Issues
None. All Series 3 features are implemented and verified.

### Next Development Tasks
Series 4 (Testing and Reliability):
1. Unit and integration tests for edge cases and input validation.
2. API failure, rate limiting, and timeout resilience handling.
3. Stress testing with large documents near the 5,000-word limit.
4. Security and reliability auditing.
