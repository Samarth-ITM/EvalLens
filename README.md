# EvalLens — Human and AI Evaluation Comparison Tool

> **Compare human ratings with automated rubric-based scores.**
>
> *Core Principle: AI assists the evaluation process. The human controls the final evaluation.*

---

## Overview

EvalLens helps teams and evaluators evaluate submitted work consistently. 

The user submits work. AI analyzes it and proposes relevant evaluation criteria. The human reviews the criteria, approves or edits them, and evaluates the work. AI can independently score the same criteria, allowing the application to compare both results for alignment and variance analysis.

---

## Current Status: Series 1 of 5 (Foundation)

This release implements **Series 1: Foundation, Architecture, and Local Setup**:
- Modular repository structure and application skeleton.
- Local SQLite database initialization with separate human and AI scoring schemas.
- BYOK (Bring Your Own Key) configuration foundation for Google Gemini with in-memory session protection.
- Streamlit multi-view navigation (Home, New Evaluation, Evaluation History, Settings).
- Full automated test suite in `TEST/`.
- Project documentation and append-only development journal in `DOCS/`.

---

## Technology Stack

- **Language:** Python (3.11+ or 3.12 recommended)
- **UI Framework:** Streamlit
- **AI Integration:** Google Gemini via the official Google GenAI Python SDK (`google-genai`)
- **Database:** SQLite (built-in standard library)
- **Data Validation:** Pydantic
- **Visualization:** Plotly
- **Testing:** pytest
- **Configuration:** Environment variables (`python-dotenv`) & local settings

---

## Repository Structure

```
EvalLens/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation & setup instructions
├── .env.example                # Template for environment configuration
├── .gitignore                  # Git exclusions for secrets, caches, and local data
│
├── config/
│   └── settings.py             # Path handling & environment settings
│
├── core/
│   ├── submission.py           # Submission parsing (Series 2)
│   ├── document_parser.py      # Document extraction (Series 2)
│   ├── ai_client.py            # Gemini BYOK client manager & connection test
│   ├── criteria_generator.py   # AI criteria suggestion (Series 2)
│   ├── rubric.py               # Rubric models & editing (Series 2)
│   ├── evaluator.py            # Evaluation workflows (Series 3)
│   ├── comparison.py           # Alignment & variance metrics (Series 3)
│   └── validators.py           # Pydantic validation schemas
│
├── database/
│   ├── db.py                   # SQLite connection, queries, & migration runner
│   └── schema.sql              # Normalized database schema
│
├── ui/
│   ├── pages/                  # Views: Home, New Evaluation, History, Settings
│   ├── components/             # Reusable UI components (Header)
│   └── styles/                 # CSS styles
│
├── DOCS/
│   ├── report.md               # Maintained project report
│   └── journal.md              # Append-only development journal
│
├── TEST/
│   ├── unit/                   # Unit test suite
│   ├── integration/            # Database and import integration tests
│   ├── fixtures/               # Test fixtures and temporary databases
│   └── README.md               # Test instructions
│
├── data/
│   └── .gitkeep                # Local SQLite storage (gitignored)
│
└── uploads/
    └── .gitkeep                # Local file uploads (gitignored)
```

---

## Local Setup & Installation

### 1. Prerequisites
- Python 3.11 or Python 3.12 (Python 3.12 recommended)
- Git

### 2. Clone and Setup Environment

#### macOS & Linux
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Windows (PowerShell)
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

*(Alternatively, if using `uv`: `uv venv --python 3.12 && source .venv/bin/activate && uv pip install -r requirements.txt`)*

### 3. Configure Environment (Optional)
```bash
cp .env.example .env
```
*Note: Setting `GEMINI_API_KEY` in `.env` is completely optional. You can enter your key directly inside the application under **Settings → AI Configuration**.*

---

## Running the Application

Launch the application with a single command:

```bash
streamlit run app.py
```

The application will start locally at `http://localhost:8501`.

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
6. **Human-Only Mode:** If no key is provided, the application remains fully functional for human-only evaluation.

