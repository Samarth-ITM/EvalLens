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

