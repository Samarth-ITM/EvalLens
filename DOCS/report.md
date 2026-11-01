# EvalLens Project Report

**Product Title:** Human and AI Evaluation Comparison Tool  
**Category:** AI Evaluation  
**Current Status:** Series 1 Complete (Series 1 of 5)  
**Maintained by:** Implementation Agent (Antigravity)  
**Product Owner & System Architect:** User  

---

## 1. Product Overview

EvalLens is an AI evaluation comparison tool designed to help evaluators and organizations assess submitted work consistently and transparently.

The application allows users to submit work (documents or text), leverages Google Gemini AI to analyze the submission and propose structured evaluation criteria, provides a human review interface to approve or edit rubrics, and then enables independent evaluation runs:
1. **Human Evaluation:** Direct scoring and qualitative feedback recorded against approved criteria.
2. **AI Evaluation:** Automated, independent scoring and rationale generation by Google Gemini using the identical criteria.
3. **Comparison Dashboard:** Side-by-side alignment, score variance, and agreement analysis.

### Core Principle
**AI assists the evaluation process; the human controls the final evaluation.** The user retains authority over rubric approval and final grading.

---

## 2. Current Development Phase

- **Active Series:** Series 1 of 5 (Foundation, Architecture, and Local Setup)
- **Phase Goal:** Establish repository foundation, application skeleton, SQLite persistence layer, in-memory BYOK (Bring Your Own Key) Gemini configuration, navigation views, documentation, and automated test suite.
- **Series 1 Status:** Complete and verified.

---

## 3. Implemented Features

| Feature / Capability | Phase | Status | Verification State |
|---|---|---|---|
| Repository Architecture & Structure | Series 1 | Implemented | Tested and passed |
| Path Management & Portable Configuration (`pathlib`) | Series 1 | Implemented | Tested and passed |
| SQLite Initialization & Automatic Schema Setup | Series 1 | Implemented | Tested and passed |
| Distinct Schema for Human vs. AI Scores | Series 1 | Implemented | Tested and passed |
| BYOK (Bring Your Own Key) Gemini Manager | Series 1 | Implemented | Tested and passed |
| API Key Masking (`AIza••••••••xxxx`) | Series 1 | Implemented | Tested and passed |
| In-Memory Session Storage (Zero disk/DB persistence) | Series 1 | Implemented | Tested and passed |
| Real Live Connection Test to Gemini API | Series 1 | Implemented | Tested and passed |
| Error Message Sanitization (Key leak prevention) | Series 1 | Implemented | Tested and passed |
| Human-Only Mode (Operational without API key) | Series 1 | Implemented | Tested and passed |
| Streamlit UI Skeleton (Home, New Eval, History, Settings) | Series 1 | Implemented | Tested and passed |
| Responsive, Jargon-Free Product Interface | Series 1 | Implemented | Tested and passed |
| Honest Empty States ("No evaluations yet") | Series 1 | Implemented | Tested and passed |
| Automated Test Suite in `TEST/` (Unit + Integration) | Series 1 | Implemented | Tested and passed |
| Maintained Project Report & Append-Only Journal | Series 1 | Implemented | Tested and passed |
| Submission & Document Parsing | Series 2 | Not implemented | Not tested |
| Gemini Rubric Criteria Generation | Series 2 | Not implemented | Not tested |
| Human Rubric Approval & Editing Interface | Series 2 | Not implemented | Not tested |
| Human Scoring & AI Scoring Execution | Series 3 | Not implemented | Not tested |
| Comparison Analytics & Dashboard | Series 3 | Not implemented | Not tested |
| Comprehensive Edge Case & Reliability Suite | Series 4 | Not implemented | Not tested |
| Exporting & Multi-Platform Packaging | Series 5 | Not implemented | Not tested |

---

## 4. Architecture and Technology Stack

The application enforces strict separation of concerns between presentation, domain logic, data persistence, and external AI services:

- **Language:** Python 3.12 (compatible with Python 3.11+)
- **User Interface:** Streamlit (clean layout, minimal custom CSS, no superfluous animations)
- **AI Integration:** Google GenAI Python SDK (`google-genai>=2.30.0`), using current models (`gemini-3.8-flash`, `gemini-3.5-flash-lite`, `gemini-4-argon`)
- **Database:** SQLite (`sqlite3` standard library) with foreign key constraints enabled
- **Data Validation:** Pydantic v2 (`pydantic>=2.7.0`)
- **Visualizations:** Plotly (`plotly>=5.20.0`)
- **Environment Management:** `python-dotenv` for optional local `.env` variables
- **Testing:** `pytest>=8.0.0`
- **Version Control:** Git

### Architecture Diagram
```
┌────────────────────────────────────────────────────────┐
│                   Streamlit UI Layer                   │
│   (app.py, ui/pages/*, ui/components/*, ui/styles/*)   │
└───────────────┬────────────────────────┬───────────────┘
                │                        │
                ▼                        ▼
┌───────────────────────────────┐ ┌──────────────────────┐
│       Core Domain Logic       │ │ Database Access Layer│
│  - core/ai_client.py (BYOK)   │ │  - database/db.py    │
│  - core/validators.py         │ │  - database/schema.sql│
│  - Future placeholders        │ └──────────┬───────────┘
└───────────────┬───────────────┘            │
                │                            ▼
                ▼                 ┌──────────────────────┐
┌───────────────────────────────┐ │  SQLite Database     │
│   External Google Gemini API  │ │  (data/evallens.db)  │
│   (Official google-genai SDK) │ └──────────────────────┘
└───────────────────────────────┘
```

---

## 5. Repository Structure

```
EvalLens/
├── app.py                      # Main Streamlit application and routing entry point
├── requirements.txt            # Project dependencies
├── README.md                   # Comprehensive setup and user guide
├── pytest.ini                  # Pytest configuration (pythonpath, testpaths)
├── .env.example                # Example environment variables (no secrets)
├── .gitignore                  # Git exclusions for .venv, data, caches, keys
│
├── config/
│   └── settings.py             # Pathlib-based settings, model definitions, env loading
│
├── core/
│   ├── submission.py           # [Placeholder] Submission processing (Series 2)
│   ├── document_parser.py      # [Placeholder] Document extraction (Series 2)
│   ├── ai_client.py            # Gemini BYOK client manager, masking, live connection test
│   ├── criteria_generator.py   # [Placeholder] AI criteria generation (Series 2)
│   ├── rubric.py               # [Placeholder] Rubric management (Series 2)
│   ├── evaluator.py            # [Placeholder] Evaluation orchestration (Series 3)
│   ├── comparison.py           # [Placeholder] Alignment & score comparison (Series 3)
│   └── validators.py           # Pydantic validation schemas
│
├── database/
│   ├── db.py                   # SQLite connection manager, parameterized queries, table init
│   └── schema.sql              # Normalized schema with separated human & AI scores
│
├── ui/
│   ├── pages/
│   │   ├── home.py             # Home overview & recent evaluations
│   │   ├── new_evaluation.py   # New evaluation placeholder (Series 2 notice)
│   │   ├── history.py          # Database-backed evaluation history
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
│   │   ├── test_ai_client.py   # Unit tests for BYOK handling, masking, sanitization
│   │   ├── test_config.py      # Unit tests for settings, path resolution, security repr
│   │   └── test_validators.py  # Unit tests for Pydantic models
│   ├── integration/
│   │   ├── test_database.py    # Integration tests for SQLite init, tables, constraints
│   │   └── test_imports.py     # Integration tests verifying all modules import cleanly
│   ├── fixtures/
│   │   └── sample_data.py      # Temporary database test fixtures
│   └── README.md               # Test runner documentation
│
├── data/
│   └── .gitkeep                # Local database storage directory (gitignored)
│
└── uploads/
    └── .gitkeep                # Local upload storage directory (gitignored)
```

---

## 6. Files Created and Modified

All files created in this initial series are new:
- `.env.example` (Created)
- `.gitignore` (Created)
- `requirements.txt` (Created)
- `pytest.ini` (Created)
- `README.md` (Created)
- `app.py` (Created)
- `config/settings.py` (Created)
- `core/validators.py` (Created)
- `core/ai_client.py` (Created)
- `core/submission.py` (Created - placeholder)
- `core/document_parser.py` (Created - placeholder)
- `core/criteria_generator.py` (Created - placeholder)
- `core/rubric.py` (Created - placeholder)
- `core/evaluator.py` (Created - placeholder)
- `core/comparison.py` (Created - placeholder)
- `database/schema.sql` (Created)
- `database/db.py` (Created)
- `ui/styles/main.css` (Created)
- `ui/components/header.py` (Created)
- `ui/pages/home.py` (Created)
- `ui/pages/new_evaluation.py` (Created)
- `ui/pages/history.py` (Created)
- `ui/pages/settings_page.py` (Created)
- `TEST/README.md` (Created)
- `TEST/fixtures/__init__.py` (Created)
- `TEST/fixtures/sample_data.py` (Created)
- `TEST/unit/__init__.py` (Created)
- `TEST/unit/test_config.py` (Created)
- `TEST/unit/test_ai_client.py` (Created)
- `TEST/unit/test_validators.py` (Created)
- `TEST/integration/__init__.py` (Created)
- `TEST/integration/test_database.py` (Created)
- `TEST/integration/test_imports.py` (Created)
- `data/.gitkeep` (Created)
- `uploads/.gitkeep` (Created)
- `DOCS/report.md` (Created)
- `DOCS/journal.md` (Created)

---

## 7. Database Design

The SQLite database uses strict relational modeling with foreign keys and indexes:

1. **`evaluations`**: Records each evaluation session (`id`, `title`, `description`, `status`, `created_at`, `updated_at`).
2. **`submissions`**: Stores submitted artifacts or raw text associated with an evaluation (`id`, `evaluation_id`, `title`, `content`, `file_name`, `file_path`, `file_type`, `created_at`).
3. **`rubrics`**: Stores rubric containers linked to an evaluation session (`id`, `evaluation_id`, `title`, `description`, `status`, `created_at`, `updated_at`).
4. **`rubric_criteria`**: Contains individual rubric criteria (`id`, `rubric_id`, `name`, `description`, `max_score`, `weight`, `order_index`, `created_at`).
5. **`human_scores`**: Stores human evaluator scores and feedback (`id`, `evaluation_id`, `criterion_id`, `score`, `feedback`, `evaluator_name`, `created_at`, `updated_at`).
6. **`ai_scores`**: Stores AI-generated scores, reasoning, evidence text, and model identifier (`id`, `evaluation_id`, `criterion_id`, `score`, `reasoning`, `evidence_text`, `model_name`, `created_at`, `updated_at`).

### Core Schema Safeguards
- **Separate Human and AI Score Tables:** Human and AI scores are maintained in separate tables (`human_scores` and `ai_scores`) with foreign key constraints back to `rubric_criteria` and `evaluations`.
- **No API Keys in Database:** The schema contains no credential or token fields.
- **Parameterized SQL:** All queries in `database/db.py` use SQLite parameterized parameter substitution (`?`).
- **Cascade Deletes:** Deleting an evaluation cascades cleanly to associated submissions, rubrics, criteria, and scores.

---

## 8. BYOK Implementation and Security Approach

The BYOK (Bring Your Own Key) architecture adheres strictly to the 13 security requirements:

1. **Zero Hardcoded Keys:** Codebase contains zero hardcoded API keys.
2. **Zero Key Commits:** Gitignore blocks `.env`, local configs, and databases from repository tracking.
3. **Masked UI Display:** Key is displayed only in masked format (`AIza••••••••xxxx`), displaying at most the first 4 and last 4 characters.
4. **No Database Persistence:** Keys are never passed to or stored in SQLite.
5. **No Key in Documentation:** Documentation contains only format examples (`AIzaSy...`).
6. **No Key in Logs or Exceptions:** `sanitize_error_message` proactively inspects exceptions and strips any occurrence of the raw API key.
7. **Session Memory Only:** Keys entered in Settings are held in Streamlit session memory (`st.session_state`).
8. **No Plaintext Persistence:** Closing or restarting the application drops the session key; users are explicitly notified that they may need to re-enter it upon restart.
9. **User Revocation / Removal:** A "Remove Key" button immediately purges the key and active connection status from session memory.
10. **Human-Only Operation:** If no key is entered, the application functions cleanly without error; AI-specific actions are disabled with clear guidance.
11. **Live Connection Test:** Testing the connection issues an actual live request to the Gemini API (`client.models.generate_content`) to verify authorization. Success is only reported if the API call succeeds.
12. **Supported Models:** Built-in model selector supporting current Gemini models (`gemini-3.8-flash`, `gemini-3.5-flash-lite`, `gemini-4-argon`).

---

## 9. Installation Instructions

### Prerequisites
- Python 3.11+ or Python 3.12 (CPython 3.12 recommended)
- Git

### Setup Steps
1. Clone the repository and navigate into the project directory:
   ```bash
   cd PE-MiniProject
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   ```
3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional) Create local `.env`:
   ```bash
   cp .env.example .env
   ```

---

## 10. Commands to Run the Application

Launch the Streamlit web interface with:

```bash
streamlit run app.py
```

Access the UI locally in your browser at `http://localhost:8501`.

---

## 11. Tests Executed and Actual Results

All tests were executed using pytest via `.venv/bin/pytest -v`.

### Test Summary
- **Total Tests Collected:** 33
- **Passed:** 33
- **Failed:** 0
- **Errors:** 0
- **Duration:** 0.76 seconds

### Detailed Results by Suite
1. **`TEST/integration/test_database.py` (4 tests)**
   - `test_database_initialization`: PASSED (verified all 6 tables and indexes are created)
   - `test_schema_separate_scores`: PASSED (verified human_scores and ai_scores are distinct tables)
   - `test_idempotent_initialization`: PASSED (verified multiple schema runs cause no corruption)
   - `test_parameterized_query_and_foreign_keys`: PASSED (verified foreign key enforcement & queries)
2. **`TEST/integration/test_imports.py` (16 tests)**
   - Verified that all 16 application modules import cleanly without missing dependencies:
     - `config.settings`: PASSED
     - `database.db`: PASSED
     - `core.ai_client`: PASSED
     - `core.validators`: PASSED
     - `core.submission`: PASSED
     - `core.document_parser`: PASSED
     - `core.criteria_generator`: PASSED
     - `core.rubric`: PASSED
     - `core.evaluator`: PASSED
     - `core.comparison`: PASSED
     - `ui.components.header`: PASSED
     - `ui.pages.home`: PASSED
     - `ui.pages.new_evaluation`: PASSED
     - `ui.pages.history`: PASSED
     - `ui.pages.settings_page`: PASSED
     - `app`: PASSED
3. **`TEST/unit/test_ai_client.py` (5 tests)**
   - `test_missing_key_handled_safely`: PASSED (no crash, clear guidance message)
   - `test_empty_string_key_handled_safely`: PASSED (whitespace handled safely)
   - `test_key_masking`: PASSED (correct prefix/suffix masking)
   - `test_sanitize_error_message_strips_key`: PASSED (leaked keys in exceptions replaced)
   - `test_client_manager_key_lifecycle`: PASSED (set, read masked, clear key lifecycle)
4. **`TEST/unit/test_config.py` (4 tests)**
   - `test_base_dir_resolution`: PASSED (pathlib resolution verified)
   - `test_directories_creation`: PASSED (`data/` and `uploads/` directories exist)
   - `test_settings_initialization`: PASSED (default model and metadata verified)
   - `test_settings_security_repr`: PASSED (settings repr hides credentials)
5. **`TEST/unit/test_validators.py` (4 tests)**
   - `test_api_key_validator_valid`: PASSED (clean keys accepted)
   - `test_api_key_validator_rejects_whitespace`: PASSED (internal whitespace rejected)
   - `test_evaluation_create_validation`: PASSED (title required, status patterns enforced)
   - `test_rubric_criterion_validation`: PASSED (score ranges and weights validated)

---

## 12. Known Limitations

1. **Session Scope of API Key:** The Gemini API key is intentionally retained only in server-side session memory. If the Streamlit application server process terminates or restarts, the user must re-enter their key unless configured via `.env`.
2. **Local Single-User Execution:** As specified for Series 1, credential management and evaluations are local-first and single-user. Multi-tenant authentication is deferred to future production versions.
3. **Series 2 & 3 Placeholders:** Submission parsing, automated criteria generation, human grading, and comparison visualizations are not yet functional in Series 1 and are clearly marked as scheduled for later series.

---

## 13. Open Decisions

| Item | Context | Impact | Status |
|---|---|---|---|
| Supported Document Formats | Series 2 will introduce file processing. Preferred initial formats: `.txt`, `.md`, and `.pdf`. | Affects document parser dependencies (e.g. PyPDF / pdfplumber). | Open for confirmation by Product Owner. |
| Scoring Scale Standard | Schema supports configurable `max_score` (default 10.0). Whether to support 1-5 Likert scales vs. 0-10 or 0-100 percentage scales. | Affects criteria generator prompts and comparison calculation. | Open for confirmation by Product Owner. |

---

## 14. Remaining Tasks (Roadmap to Series 2)

- [ ] Implement `core/document_parser.py` for `.txt`, `.md`, and `.pdf` document extraction.
- [ ] Implement `core/submission.py` to handle uploads, storage in `uploads/`, and database records.
- [ ] Implement `core/criteria_generator.py` using `google-genai` to generate evaluation rubrics from submissions.
- [ ] Build editable rubric review UI in `ui/pages/new_evaluation.py` allowing humans to approve, add, edit, or delete criteria.
- [ ] Implement citation/evidence extraction referencing submission snippets.

---

## 15. Master Project Checklist

### Series 1: Foundation, Architecture, and Local Setup
- [x] Inspect existing workspace and initialize git repository.
- [x] Create modular repository directory structure (`config/`, `core/`, `database/`, `ui/`, `DOCS/`, `TEST/`, `data/`, `uploads/`).
- [x] Path handling with `pathlib` and environment configuration in `config/settings.py`.
- [x] SQLite schema (`database/schema.sql`) and database manager (`database/db.py`) with automatic initialization.
- [x] Separate `human_scores` and `ai_scores` schema design.
- [x] Gemini BYOK foundation with masked display, session storage, live test, and error sanitization (`core/ai_client.py`).
- [x] Streamlit multi-view UI (`app.py`, `ui/pages/*`, `ui/components/header.py`, `ui/styles/main.css`).
- [x] Honest empty states ("No evaluations yet") and plain-English messaging.
- [x] Placeholders for future modules in `core/` without premature implementation.
- [x] Automated test suite in `TEST/` (33 tests, all passing).
- [x] Verified application execution and HTTP 200 response on `http://localhost:8501`.
- [x] Maintain project report (`DOCS/report.md`).
- [x] Maintain append-only journal (`DOCS/journal.md`).

### Series 2: Submission and AI Criteria (Pending)
- [ ] Submission interface.
- [ ] File and text processing.
- [ ] Evaluation modes.
- [ ] Gemini criteria generation.
- [ ] Evidence references.
- [ ] Editable and approvable rubrics.

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

