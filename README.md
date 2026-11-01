# EvalLens — Human and AI Evaluation Comparison Tool

> **Compare human ratings with automated rubric-based scores.**
>
> *Core Principle: AI assists the evaluation process. The human controls the final evaluation.*

---

## Overview

EvalLens helps teams and evaluators evaluate submitted work consistently. 

The user submits work. AI analyzes it and proposes relevant evaluation criteria. The human reviews the criteria, approves or edits them, and evaluates the work. AI can independently score the same criteria, allowing the application to compare both results for alignment and variance analysis.

---

## Current Status: Series 2 of 5 (Submission and AI Criteria Generation)

This release implements **Series 2**:
- Document and text parsing for 13 supported file types (`.txt`, `.md`, `.pdf`, `.docx`, `.py`, `.cpp`, `.h`, `.hpp`, `.java`, `.js`, `.ts`, `.json`, `.html`, `.css`, `.sql`).
- Strict 5,000 combined word limit enforcement and 10 MB per-file limits.
- Separation of contextual reference materials from graded submission content.
- AI criteria generation with Google Gemini using 3 prompt versions (V1 basic, V2 with instructions, V3 evidence-grounded default).
- Evidence grounding: verbatim quotations and line/page references extracted directly from the submission.
- Complete human review interface: edit names, descriptions, max marks, evidence guidance; add, remove, and reorder criteria.
- Explicit rubric approval workflow with SQLite persistence, distinguishing AI proposals from human-approved rubrics.
- Full human-only fallback mode without requiring a Gemini key.

---

## Technology Stack

- **Language:** Python (3.11+ or 3.12 recommended)
- **UI Framework:** Streamlit
- **AI Integration:** Google Gemini via the official Google GenAI Python SDK (`google-genai`)
- **Document Extraction:** `pypdf` (PDF extraction) and `python-docx` (DOCX extraction)
- **Database:** SQLite (`sqlite3` standard library) with foreign key constraints enabled
- **Data Validation:** Pydantic v2
- **Visualization:** Plotly
- **Testing:** pytest
- **Configuration:** Environment variables (`python-dotenv`) & local settings

---

## Supported Document Formats & Limits

| Format Category | Supported Extensions | Notes |
|---|---|---|
| Text & Markdown | `.txt`, `.md` | Line numbers tracked |
| Documents | `.pdf`, `.docx` | PDF page markers preserved; DOCX paragraphs & tables extracted |
| Source Code | `.py`, `.cpp`, `.h`, `.hpp`, `.java`, `.js`, `.ts`, `.json`, `.html`, `.css`, `.sql` | Inspected strictly as text; line numbers tracked |

- **Word Limit:** Maximum 5,000 words total per evaluation (combined across pasted text and all uploaded files). Submissions exceeding 5,000 words are rejected with the detected count.
- **File Size Limit:** 10 MB per file.
- **Unsupported Formats:** ZIP, PPTX, image formats, and OCR are not supported in this prototype. Scanned image-only PDFs produce an informative warning.

---

## Workflow Guide: Creating an Evaluation & Approving a Rubric

### 1. Configure Gemini Key (Optional for Human-Only Mode)
- Open **Settings → AI Configuration**.
- Enter your Google Gemini API key and click **Save Key**.
- Click **Test Connection** to verify live connectivity with Gemini.
- *Note: You can skip this step if you wish to build custom rubrics manually.*

### 2. Create a New Evaluation
- Navigate to **New Evaluation**.
- Enter an **Evaluation Title** (e.g. `CS101 Final Project Review`).
- Select a **Submission Type** (`Written Work`, `Code`, `Software Project`, `Technical Report`, `Custom`).
- (Optional) Enter **Evaluation Instructions** and **Reference Material** (e.g. assignment guidelines; kept separate from the submission).
- Paste submission text, upload one or multiple supported files, or combine both.
- Select your AI Prompt Strategy (default: `V3`).

### 3. Generate or Create Criteria
- Click **Analyze with Gemini AI** to generate 3–8 evidence-grounded criteria with verbatim excerpts and location references.
- Alternatively, click **Create Rubric Manually** to build your criteria from scratch without an AI key.

### 4. Review and Edit Rubric
- Edit criterion names, descriptions, and scoring guidance.
- Adjust maximum marks per criterion (total marks are automatically recalculated).
- Use **⬆️ Up** and **⬇️ Down** buttons to reorder criteria.
- Add additional custom criteria with **➕ Add Criterion** or remove criteria with **🗑️ Delete**.

### 5. Approve Rubric
- Click **Approve Rubric**. The evaluation session, submission files, and approved criteria are safely stored in the local SQLite database.
- Review your approved evaluations under **Evaluation History**.

---

## Local Setup & Installation

### 1. Prerequisites
- Python 3.11 or Python 3.12 (Python 3.12 recommended)
- Git

### 2. Clone and Setup Environment

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
Visit `http://localhost:8501` in your browser.

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
2. **Session Memory Only:** Keys entered in the Settings UI remain exclusively in server memory during the active session.
3. **No Database Persistence:** Keys are never written to the SQLite database or saved to disk files.
4. **Masked Display:** The UI masks active keys (e.g. `AIza••••••••1234`).
5. **No Key Leakage:** Error messages strip and sanitize API keys to prevent accidental leaks in UI or logs.
6. **Human-Only Mode:** If no key is provided, the application remains fully functional for manual rubric creation.
