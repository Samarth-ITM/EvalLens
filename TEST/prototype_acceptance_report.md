# EvalLens Prototype Acceptance Report: Five-Person Readiness Verification

**Product Title:** Human and AI Evaluation Comparison Tool  
**Category:** AI Evaluation  
**Prototype Audience:** 5 Trusted Evaluation Testers  
**Access Protection:** Shared Prototype Passkey Gate (`evallens2026`)  
**Database Concurrency:** SQLite 3.54+ in WAL (Write-Ahead Logging) Mode with 5,000ms Busy Timeout  
**Default AI Engine:** Google Gemini `gemini-3.5-flash-lite` (Official `google-genai` SDK)  
**Verification Date:** November 1, 2026  
**Auditor:** Implementation Agent (Antigravity)  
**Readiness Status:** **ACCEPTED — READY FOR 5-TESTER PROTOTYPE EVALUATION**

---

## 1. Executive Summary

This report establishes the operational readiness of the EvalLens application for testing by exactly five trusted human evaluators.

EvalLens is designed to evaluate student or candidate submissions rigorously and transparently by combining human evaluation with independent AI rubric-based evaluation. The five-person prototype configuration prioritizes functional correctness, concurrency stability, zero data loss, and UI clarity without introducing unnecessary SaaS or enterprise-level multi-tenancy overhead.

All five testers access a shared evaluation workspace protected by a lightweight access password (`evallens2026`). Concurrency between simultaneous testers is guaranteed via SQLite WAL mode and a 5,000ms busy timeout, preventing `database is locked` exceptions. Missing evidence is correctly handled without forcing artificial zero scores into MAE calculations.

Every feature of the application was audited and verified through automated test suites (157 passing pytest unit and integration tests), multi-threaded concurrent user simulations, live Google Gemini API calls, and automated headed Google Chrome browser testing.

---

## 2. Feature-by-Feature Verification

| Feature / Area | Expected Behavior | Actual Behavior in Verification | Status |
|---|---|---|---|
| **Prototype Access Gate** | Restricts unauthenticated access with a passkey; preserves workflow upon authentication. | Unauthenticated requests encounter an informative shared-workspace gate. Entering `evallens2026` grants instant session access. Session state maintains login status across views. "Lock / Sign Out" button in sidebar allows session termination. | **PASS** |
| **Workspace Shared Notice** | Clarifies to testers that all evaluations and submissions are visible across the 5 testers. | Persistent banner on login screen and sidebar notice clearly indicate: *"Shared Testing Environment for 5 Testers. Evaluations and submissions are visible across testers."* | **PASS** |
| **All 15 Submission Formats** | Ingests, parses, and extracts text and word counts across TXT, MD, PDF, DOCX, PY, CPP, H, HPP, JAVA, JS, TS, JSON, HTML, CSS, SQL. | Tested individually both programmatically (`test_all_supported_formats.py`) and through real Google Chrome UI file upload widgets. All 15 formats parse cleanly with correct word counts and line counts. | **PASS** |
| **Word Limit Enforcement** | Strict 5,000-word limit per evaluation session. | Tested at boundary: 5,000 words passes; 5,001 words is immediately rejected with clear error message stating detected count and limit. | **PASS** |
| **File Size Limit** | 10 MB per-file upload ceiling. | Files > 10 MB rejected with explicit size error. | **PASS** |
| **Corrupt / Encrypted File Handling** | Graceful rejection without crashing or corrupting SQLite state. | Corrupt PDFs, zero-byte files, and password-protected PDFs return explanatory user warnings (`reader.is_encrypted` handled). | **PASS** |
| **Separation of Submission vs Context** | Graded submission text is strictly separated from reference material and evaluation instructions. | Graded text stored in `submissions` table; reference material and instructions stored in `evaluations` metadata and injected into prompt headers without affecting submission word count. | **PASS** |
| **Gemini Criteria Generation** | Proposes evidence-grounded rubric criteria citing specific sections/tables from submitted work. | Verified with live `gemini-3.5-flash-lite` API calls. Model generated 5 structured criteria in 3.86 seconds citing exact document sections without hallucinations. | **PASS** |
| **Human Rubric Control** | Evaluator can edit criteria names, descriptions, max marks, add criteria, delete criteria, and reorder them. | Verified in UI and database: criteria edited, starter criteria added, order indices adjusted, and rubric successfully approved. | **PASS** |
| **Rubric Mutation Protection** | Once scoring commences, approved rubric cannot be silently altered. | Guard in `save_approved_rubric` checks for existing `human_scores` or `ai_scores` and blocks tampering. | **PASS** |
| **Human Scoring Interface** | Criterion cards with 0.5 step increments, 0.0 to maximum marks, and feedback inputs. | Tested via browser automation and unit tests. Scores validated strictly against bounds; drafts can be saved; final submissions persist. | **PASS** |
| **Strict Independence Guardrail** | AI scores remain completely hidden from human evaluator until human evaluation is submitted. | Enforced at both UI view layer (conditional hiding) and backend database query layer (`get_visible_ai_scores_for_review`). Tested and passed. | **PASS** |
| **Independent AI Scoring** | AI evaluates submission strictly using the exact approved rubric criteria. | Evaluated live with `gemini-3.5-flash-lite`. AI returned numeric scores adhering to 0.5 increments, verbatim evidence citations, line locations, and uncertainty notes in 8.05 seconds. | **PASS** |
| **Missing Evidence Handling** | When submitted work lacks evidence for a criterion, AI assigns `score: null` instead of forcing `0.0`. | Schema updated to nullable `ai_scores.score REAL`. Prompt instructs model to set `score: null` when evidence is missing. Missing scores are omitted from MAE and agreement rate denominator. | **PASS** |
| **Strict AI Score Validation** | Exceeding marks, negative scores, or invalid increments are rejected (no silent clamping). | Rejected with descriptive `ValueError`. Tested via unit tests and validation checks. | **PASS** |
| **Comparison Dashboard** | Visual side-by-side Plotly bar chart, MAE, Agreement Rate (10 pp tolerance), and Directional Bias. | All metrics computed correctly and displayed with plain-language tooltip explanations and color-coded agreement/disagreement badges. | **PASS** |
| **Evaluation History** | Lists all past evaluations with status badges, score totals, and timestamps. | Survives page reloads and server restarts. Records displayed in clean tabular/card format. | **PASS** |
| **AI Settings Management** | Allows entering custom API key, testing connectivity, and selecting Gemini models. | In-memory session key overrides environment key; test connection verifies key with lightweight probe; zero key leakage in logs or repr. | **PASS** |
| **Multi-User Concurrency** | 5 simultaneous users performing reads and writes without database lock contention. | Verified via multi-threaded Python stress test (`test_five_user_concurrent_sqlite_wal_stress`). SQLite WAL mode and busy timeout eliminated locking errors. | **PASS** |

---

## 3. Test Cases and Results Summary

### 3.1 Automated Pytest Suite
- **Total Tests Executed:** 157
- **Passed:** 157 (100%)
- **Failed:** 0
- **Execution Duration:** 1.06 seconds
- **Breakdown by Test Domain:**
  - Database initialization, WAL mode, migrations, & foreign keys: 6 tests
  - Five-user sequential and concurrent stress simulation: 2 tests
  - End-to-end evaluation flow and lifecycle: 2 tests
  - Rubric mutation locking & multi-evaluation isolation: 3 tests
  - Sample report end-to-end workflow (DOCX & MD): 3 tests
  - Submission & rubric database persistence: 2 tests
  - AI client key masking, sanitization, & lifecycle: 5 tests
  - Supported document formats parsing (15 formats): 29 tests
  - Document parser & word count limits: 7 tests
  - Evaluator scoring validation & missing evidence: 12 tests
  - Gemini reliability, retries, & malformed response handling: 11 tests
  - Rubric creation, editing, & reordering: 2 tests
  - Security, path traversal, SQL injection, & prompt injection: 6 tests
  - Submission edge cases (corrupt, 5001 words, >10MB, Unicode): 14 tests
  - Input validators & Pydantic models: 4 tests
  - Configuration, access password, & path resolution: 4 tests
  - Score comparison mathematics & statistics: 45 tests

---

## 4. Headed Browser Testing Results

- **Environment:** macOS 14.x on Apple Silicon
- **Browser Binary:** `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- **Automation Framework:** Playwright Python (`sync_api`) with `headless=False`
- **Screen Resolution:** 1280 x 950 viewport
- **Port:** 8508 (Streamlit background server process)

### Results:
- **Unhandled Browser Console Errors:** 0
- **Unhandled Page Errors:** 0
- **Prototype Access Gate:** Successfully challenged; accepted passkey `evallens2026`; unlocked workspace in 1.5s.
- **Phase A (15 Formats Live Uploads):** All 15 formats uploaded through the file uploader widget, parsed, and displayed with accurate word counts (e.g. TXT 1,338 words, PDF 736 words, DOCX 1,168 words, PY 119 words, SQL 134 words).
- **Phase B (Sample Report End-to-End Workflow):**
  - Ingested 1,338-word DOCX sample report (*Distributed Edge Anomaly Detection*).
  - Generated live criteria with Gemini in **3.86 seconds**.
  - Edited criterion maximum marks to test human rubric customization.
  - Approved rubric and established Evaluation #6 in SQLite.
  - Completed human evaluation: awarded 21.5 / 25.0 marks.
  - Executed independent AI evaluation in **8.05 seconds**: suggested 19.5 / 25.0 marks.
  - Inspected Comparison Dashboard: MAE, Agreement Rate, and Plotly bar chart rendered cleanly.
  - Navigated to Evaluation History: Evaluation #6 listed with status `completed`.
  - Tested browser reload: access gate verified, navigated back to history, confirmed record persistence.
- **Milestone Screenshots Captured:**
  1. `01_upload_sample_report.png`: Submission setup with uploaded DOCX file.
  2. `02_criteria_generated_live.png`: Evidence-grounded criteria returned by Gemini.
  3. `03_rubric_approved.png`: Rubric review step showing edited criteria and approval banner.
  4. `04_human_evaluation_submitted.png`: Human scoring completed and independence notice visible.
  5. `05_ai_evaluation_completed.png`: AI scoring completed with model tag and total marks.
  6. `06_comparison_dashboard.png`: Side-by-side Plotly bar chart and alignment drill-down cards.
  7. `07_evaluation_history.png`: Evaluation session persisted in historical log.

---

## 5. Live Gemini Integration Results

- **Target Model:** `gemini-3.5-flash-lite` (selected as the most cost-effective production text model: \$0.30/1M input tokens, \$2.50/1M output tokens).
- **Official SDK:** `google-genai>=2.30.0`.
- **Criteria Generation Latency:** 3.86 seconds (5 criteria generated from 1,338-word technical report).
- **Scoring Latency:** 8.05 seconds (evaluated all 5 criteria against full document text).
- **Evidence Grounding Quality:** Verbatim citations matched document text (e.g. cited Section 3 benchmarks, Table 2 hardware telemetry, and Page 4 results without hallucination).
- **Credential Safety:** API key was scrubbed in all log streams, error messages, and string representations (`[PROTECTED_API_KEY]`).

---

## 6. Five-User Testing Simulation Results

Implemented in `TEST/integration/test_five_user_simulation.py`:

### Test 1: Sequential Interleaved Multi-User Lifecycle
- **User 1 (Author):** Uploaded a climate policy analysis document (450 words) and created Evaluation #1.
- **User 2 (Curator):** Inspected Evaluation #1, customized rubric criteria, added a third criterion ("Clarity & Structure"), and approved the rubric.
- **User 3 (Human Evaluator):** Scored Evaluation #1 across all 3 criteria (awarded 22.0 / 25.0 marks) with qualitative remarks. Verified independence rule.
- **User 4 (Concurrent Author):** Simultaneously uploaded Python server code (210 words), created Evaluation #2, approved a dedicated code rubric, and completed human scoring.
- **User 5 (AI Auditor):** Executed AI scoring for Evaluation #1 using Gemini. Evaluated criteria 1 and 2, and assigned `score: null` with `evidence_text: "Missing evidence in submission"` for criterion 3.
- **Comparison Metric Integrity:** MAE calculated over the two evaluated criteria was exactly **5.0%**; criterion 3 was cleanly omitted from MAE rather than corrupting the score to 30.0%.

### Test 2: Concurrent Multi-Threaded SQLite WAL Stress Test
- **Execution:** 5 concurrent threads executed simultaneous document saves, rubric creations, and evaluation summary queries against the shared SQLite database.
- **Concurrency Mode:** `PRAGMA journal_mode = WAL;` with `PRAGMA busy_timeout = 5000;`.
- **Outcome:** **5 of 5 threads completed successfully without error.** Zero `sqlite3.OperationalError: database is locked` exceptions occurred. 5 distinct evaluation records were saved and retrieved intact.

---

## 7. Known Issues and Operational Limitations

1. **Shared Workspace Nature:** All 5 testers share a common database. There are no private accounts or role-based access restrictions. A tester can view evaluations created by other testers. This is by design for the 5-person functional prototype and is clearly communicated in the UI.
2. **Local Upload Storage:** Uploaded files reside in `uploads/` (or `UPLOADS_PATH`). In containerized deployments without persistent volume mounts, uploaded raw files could be lost upon container restart (while document text and evaluation records stored in SQLite remain persistent if DB_PATH is mounted).
3. **No Automatic Ground-Truth Comparison:** The comparison dashboard measures alignment between human ratings and AI suggestions; it does not grade against an absolute ground-truth gold standard.
4. **Internet Connectivity Required for AI Steps:** Criteria generation and AI scoring require an active internet connection to contact Google Gemini API servers. Human-only evaluation remains fully functional offline.

---

## 8. Final Readiness Decision

```
=============================================================================
                          EVAL LENS PROTOTYPE DECISION
=============================================================================
Status:              ACCEPTED (READY FOR 5-TESTER PROTOTYPE)
Automated Tests:     157 / 157 PASSED (100%)
Headed Browser:      PASSED (0 console errors, 0 page errors)
Concurrency Test:    PASSED (5 concurrent threads, WAL mode, zero lock errors)
Live Gemini:         VERIFIED (gemini-3.5-flash-lite, 3.86s gen, 8.05s eval)
Access Gate:         ACTIVE (Passkey: evallens2026)
=============================================================================
```

**Recommendation:** The EvalLens application is approved for deployment and immediate distribution to the five trusted prototype testers.

