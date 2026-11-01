# EvalLens — Human and AI Evaluation Comparison Tool

**Distributable Release Package (FINAL_BUILD)**  
*Compare human evaluation with automated rubric-based AI scores.*

---

## Overview

EvalLens helps evaluators evaluate submitted work consistently, rigorously, and transparently:
1. Ingests submitted student or candidate work across **15 supported formats** (TXT, MD, PDF, DOCX, PY, CPP, H, HPP, JAVA, JS, TS, JSON, HTML, CSS, SQL) up to 5,000 words.
2. Uses Google Gemini AI to analyze work and propose evidence-grounded rubric criteria citing specific document excerpts.
3. Allows human evaluators full control to review, edit, reorder, and explicitly approve the rubric.
4. Enforces a strict **Independence Guardrail**: AI suggestions remain strictly locked and invisible until the human evaluation is submitted.
5. Performs optional independent AI scoring against the approved rubric with verbatim citations and uncertainty notes.
6. Computes comparison analytics (Mean Absolute Error, Agreement Rate within 10 percentage points, Signed Directional Bias, Pearson correlation) and visualizes alignment in a side-by-side Plotly dashboard.

> [!IMPORTANT]
> **Five-Person Prototype Notice:**  
> EvalLens is configured as a private evaluation prototype for five trusted testers. All five testers share a common workspace. Submissions, rubrics, and evaluations are visible across testers. Please do not submit confidential or sensitive personal data.

---

## Running EvalLens

### Method A: Docker (Recommended for Local Portability)

Run a clean, isolated container with persistent storage on any computer with Docker Desktop.

#### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

#### Steps
1. **Extract the Package:**
   Extract `FINAL_BUILD.zip` or open the `FINAL_BUILD/` folder in your terminal.
2. **Configure Environment:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Open `.env` in any text editor and optionally add your `GEMINI_API_KEY`:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   EVALLENS_ACCESS_PASSWORD=evallens2026
   ```
   *(If you leave `GEMINI_API_KEY` blank, you can enter it later inside the app under **Settings → AI Configuration**).*
3. **Build and Launch Container:**
   ```bash
   docker compose up --build -d
   ```
4. **Access the Application:**
   Open your browser and navigate to:
   [http://localhost:8501](http://localhost:8501)
5. **Unlock the Workspace:**
   Enter the prototype access passkey: `evallens2026` (or the password configured in `.env`).
6. **Data Persistence:**
   Evaluation data and uploaded files are saved to Docker persistent volumes (`evallens-data` and `evallens-uploads`). Restarting or stopping the container (`docker compose down`) will **not** delete your evaluations.
7. **Stop Container:**
   ```bash
   docker compose down
   ```

---

### Method B: Render Cloud Deployment (Hosted URL for 5 Testers)

Deploy EvalLens as a private hosted web service so your five testers can access it from any browser without installing Python, Docker, or Git.

#### Steps
1. **Push to GitHub:**
   Initialize a Git repository inside `FINAL_BUILD/` and push it to a private GitHub repository:
   ```bash
   cd FINAL_BUILD
   git init
   git add .
   git commit -m "Initial EvalLens deployable build"
   git remote add origin https://github.com/<your-username>/evallens.git
   git push -u origin main
   ```
2. **Connect to Render:**
   - Log into your [Render Dashboard](https://dashboard.render.com).
   - Click **New +** → **Blueprint** (to deploy automatically using `render.yaml`), OR select **New +** → **Web Service**.
3. **Configure Web Service (if configuring manually):**
   - **Environment:** `Python 3`
   - **Build Command:**
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
     ```
   - **Health Check Path:** `/_stcore/health`
   - **Instance Type:** `Starter` plan (required for persistent disk attachment).
4. **Configure Environment Variables in Render Dashboard:**
   - `EVALLENS_ENV` = `render`
   - `EVALLENS_ACCESS_PASSWORD` = Set a strong private passkey for your 5 testers.
   - `GEMINI_API_KEY` = Your Google Gemini API key.
   - `GEMINI_MODEL` = `gemini-3.5-flash-lite`
   - `DB_PATH` = `/var/data/evallens.db`
   - `UPLOADS_PATH` = `/var/data/uploads`
5. **Attach Persistent Storage Disk:**
   - In your Web Service settings, scroll down to **Disks**.
   - Click **Add Disk**.
   - **Name:** `evallens-storage`
   - **Mount Path:** `/var/data`
   - **Size:** `1 GB` (ample for hundreds of evaluation sessions).
   - *Note:* Persistent disks ensure evaluations and uploads survive service redeployments.
6. **Deploy:**
   Click **Create Web Service** / **Deploy**. Render will install dependencies and start the Streamlit server.
7. **Share with Testers:**
   Provide your testers with the live Render URL (e.g. `https://evallens.onrender.com`) and your custom `EVALLENS_ACCESS_PASSWORD`.

---

### Method C: Local Python Execution

If you prefer to run directly in a Python environment without Docker:

```bash
# 1. Create and activate a Python 3.11 or 3.12 virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Create .env configuration
cp .env.example .env

# 4. Launch Streamlit
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) and enter `evallens2026`.

---

## Supported File Formats (15 Total)

EvalLens supports parsing single or multiple files combined with pasted text up to **5,000 words total**:
- **Text & Markup:** `.txt`, `.md`, `.html`, `.css`, `.json`, `.sql`
- **Documents:** `.pdf` (text-based), `.docx`
- **Programming Languages:** `.py`, `.java`, `.cpp`, `.h`, `.hpp`, `.js`, `.ts`

Maximum single file size: **10 MB**.

---

## Google Gemini API Configuration (BYOK)

- **Official SDK:** `google-genai>=2.30.0`.
- **Default Model:** `gemini-3.5-flash-lite` (\$0.30 / 1M input tokens, \$2.50 / 1M output tokens).
- **Security Guarantee:** API keys entered via the UI are kept strictly in session memory (`st.session_state`) and are **never** written to SQLite or stored on disk.
- **Offline / Human-Only Mode:** If no API key is provided, all human evaluation, rubric customization, scoring, and history features work 100% offline.

---

## Project Structure

```
FINAL_BUILD/
├── app.py                     # Main application entry point & access gate
├── config/
│   ├── __init__.py
│   └── settings.py            # Path resolution & environment settings
├── core/
│   ├── __init__.py
│   ├── ai_client.py           # Gemini API manager, transient retries & masking
│   ├── comparison.py          # MAE, agreement rate, and bias statistics
│   ├── criteria_generator.py  # Grounded rubric proposal generator
│   ├── document_parser.py     # Parser for all 15 supported file formats
│   ├── evaluator.py           # Human & AI score validation and execution
│   ├── rubric.py              # Rubric state management and approval
│   ├── submission.py          # Submission aggregation and file persistence
│   └── validators.py          # Pydantic schema models
├── database/
│   ├── __init__.py
│   ├── db.py                  # SQLite WAL connections & transactions
│   └── schema.sql             # Relational table schema
├── ui/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   └── header.py          # Application header banner
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── evaluate.py        # Human scoring & comparison dashboard
│   │   ├── history.py         # Evaluation history view
│   │   ├── home.py            # Home overview & recent evals
│   │   ├── new_evaluation.py  # Submission & criteria workflow
│   │   └── settings_page.py   # AI BYOK settings
│   └── styles/
│       └── main.css           # Styling
├── .streamlit/
│   └── config.toml            # Server address 0.0.0.0 & theme config
├── Dockerfile                 # Production multi-stage Docker build
├── docker-compose.yml         # Container & volume orchestration
├── .dockerignore
├── .gitignore
├── .env.example               # Template environment configuration
├── render.yaml                # Render Infrastructure-as-Code blueprint
└── README.md                  # This documentation
```

