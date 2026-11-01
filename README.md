# EvalLens — Human and AI Evaluation Comparison Tool

> **Compare human ratings with automated rubric-based scores.**
>
> *Core Principle: AI assists the evaluation process. The human controls the final evaluation.*

---

## Overview

EvalLens helps teams and evaluators evaluate submitted work consistently, rigorously, and transparently.

The workflow begins by accepting submissions across 13 formats. Google Gemini AI analyzes the work to propose structured, evidence-grounded criteria. The human evaluator reviews and explicitly approves the rubric. Human evaluation is conducted independently, followed by optional AI evaluation on the exact approved rubric. The application compares both evaluations to highlight alignment and variance without ever treating AI scores as ground truth.

---

## Current Status: Series 3 of 5 (Human Evaluation, AI Evaluation and Comparison)

This release implements **Series 3**:
- **Human Evaluation Interface:** Grade approved rubric criteria with 0.5 decimal increments, validated bounds `[0, max_marks]`, and optional qualitative remarks.
- **Independence Guardrail:** AI scores and suggestions remain strictly hidden from the evaluator until human evaluation is officially submitted.
- **Independent AI Evaluation:** Optional Gemini scoring using the exact approved rubric criteria (no criteria modification or hallucinations).
- **Comparison Analytics:** Normalized scores, raw absolute differences, normalized absolute differences, Mean Absolute Error (MAE), and agreement rate within a 10 percentage-point tolerance.
- **Comparison Dashboard:** Plotly visual bar chart and expandable criterion-level comparison table highlighting areas of significant disagreement.
- **Human-Only Evaluation Support:** Full evaluation workflow functions without a Gemini key; human results display cleanly without AI comparisons.
- **Relational Persistence:** Separate SQLite persistence for `human_scores` and `ai_scores` preserving historical evaluations.

---

## Technology Stack

- **Language:** Python (3.11+ or 3.12 recommended)
- **UI Framework:** Streamlit
- **Visualizations:** Plotly
- **AI Integration:** Google Gemini via the official Google GenAI Python SDK (`google-genai`)
- **Document Extraction:** `pypdf` (PDF extraction) and `python-docx` (DOCX extraction)
- **Database:** SQLite (`sqlite3` standard library) with foreign keys and migrations
- **Data Validation:** Pydantic v2
- **Testing:** pytest
- **Configuration:** Environment variables (`python-dotenv`) & local settings

---

## Supported Document Formats & Limits

| Format Category | Supported Extensions | Notes |
|---|---|---|
| Text & Markdown | `.txt`, `.md` | Line numbers tracked |
| Documents | `.pdf`, `.docx` | PDF page markers preserved; DOCX paragraphs & tables extracted |
| Source Code | `.py`, `.cpp`, `.h`, `.hpp`, `.java`, `.js`, `.ts`, `.json`, `.html`, `.css`, `.sql` | Inspected strictly as text; line numbers tracked |

- **Word Limit:** Maximum 5,000 words total per evaluation (combined across pasted text and all uploaded files).
- **File Size Limit:** 10 MB per file.
- **Unsupported Formats:** ZIP, PPTX, image formats, and OCR are not supported in this prototype.

---

## Evaluation and Comparison Workflow

### 1. Create Evaluation & Approve Rubric
- Navigate to **New Evaluation**.
- Enter a title, choose submission type, and add optional instructions/reference materials.
- Paste text, upload files, or combine both.
- Generate criteria using Gemini (with V3 prompt strategy by default) or build custom criteria manually.
- Review, edit, reorder, and click **Approve Rubric**.

### 2. Enter Human Scores
- Open the evaluation in the **Evaluate** tab (or via **Evaluation History**).
- For each approved criterion, review description, evidence guidance, and grounded excerpts.
- Enter a score between 0 and the criterion's maximum marks (in 0.5 increments).
- Enter optional qualitative feedback for each criterion.
- Click **Submit Human Evaluation** (or **Save Progress** to draft).
- *Note: AI scores remain hidden until human submission is confirmed.*

### 3. Optional AI Evaluation
- Once human scores are submitted, click **Run AI Evaluation with Gemini**.
- Gemini independently evaluates the submission against the exact approved rubric criteria and returns suggested scores, justifications, and evidence excerpts.

### 4. Review Comparison Dashboard
- Compare overall metrics: Human Total, AI Suggestion, Score Difference, MAE, and Agreement Rate.
- Inspect the interactive Plotly bar chart comparing human scores vs AI suggestions per criterion.
- Drill down into individual criteria in the comparison table to inspect human feedback alongside AI reasoning, cited evidence, and uncertainty notes.
- Criteria with normalized differences exceeding 10 percentage points are flagged as significant disagreement.

---

## Local Setup & Installation

### 1. Prerequisites
- Python 3.11 or Python 3.12 (Python 3.12 recommended)
- Git

### 2. Setup Environment

```bash
# Clone and enter repo
cd PE-MiniProject

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate       # macOS / Linux
# or .venv\Scripts\Activate.ps1 # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application

```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## Running the Tests

Execute the automated test suite with pytest:

```bash
pytest TEST/ -v
```

---

## BYOK Security Guardrails

EvalLens is designed with privacy and security as primary principles:
1. **Never Hardcoded:** No API keys are embedded in source code.
2. **Session Memory Only:** Keys entered in Settings remain exclusively in server memory during the active session.
3. **No Database Persistence:** Keys are never written to SQLite or saved to disk files.
4. **Masked Display:** The UI masks active keys (e.g. `AIza••••••••1234`).
5. **No Key Leakage:** Error messages strip and sanitize API keys to prevent accidental leaks in UI or logs.
6. **Human-Only Mode:** If no key is provided, the application remains fully functional for human-only evaluation.
