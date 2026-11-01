# EvalLens: Human & AI Evaluation Comparison System

**EvalLens** is a modern, high-performance web application designed for educators, examiners, and academic evaluators to systematically compare human judgment with Google Gemini AI evaluations.

---

### 🎓 Academic Submission Metadata
* **Student Name:** Samarth Navale
* **Roll Number:** 150096725148
* **Subject:** AI Prompt Engineering
* **Professor:** Poonam Ma'am
* **Cohort:** Sam Altman
* **Project:** Final Evaluator & Dual Human-AI Grading Comparison System

---

## 🚀 Quick Start for Evaluation & Testing

You can run EvalLens immediately with zero complex setup.

### 1. Install Dependencies
```bash
npm install
```

### 2. Start the Development Server
```bash
npm run dev
```
Open **`http://localhost:5173`** in any web browser.

### 3. Log In with Prototype Passkey
* **Default Passkey:** `evallens2026`
* Click **Access Workspace** to enter.

---

## 📦 Production Build & Teacher Delivery

A production-ready build has already been generated in the **`dist/`** directory.

To test the compiled production build locally:
```bash
npm run build
npm run preview
```
The application runs as a fully optimized, standalone single-page application (SPA).

---

## 🌟 Core Features & Evaluation Workflow

```
1. Ingest Document  ➔  2. Calibrate Rubric  ➔  3. Examiner Reading  ➔  4. AI Critique  ➔  5. Dual Comparison
```

### 1. Document Ingestion & Word Count Verification
* Upload documents (`.txt`, `.md`, `.py`, `.sql`, `.docx`, `.pdf`) or paste text directly.
* Real-time word counter with strict validation (5,000 words limit).
* Automatic title suggestion based on document headers.

### 2. Micro-Explainer Walkthrough
* An animated 3-step guide on the Home dashboard explaining the workflow.
* Includes a **Skip Guide** button that permanently saves your preference in `localStorage`.

### 3. Examiner Document Reading Sheet (A4 Paper View)
* Located on the **Evaluate** screen.
* Displays the submitted document in an authentic physical paper sheet layout.
* **Toggleable Line Numbers (`#`)** for line-by-line verification.
* **Font Zoom Controls (`+ / -`)** for readability.
* **One-Click Text Copy** and **Estimated Reading Time**.
* **Side-by-Side Split View:** Examiners can read the document on the left and enter marks on the right simultaneously.

### 4. Context-Grounded AI Scoring & Critique
For every criterion, the system displays three distinct, context-relevant sections:
* **AI Suggested Mark:** Realistic marks with natural variance (e.g. `4.5 / 5`, `3.5 / 5`, `4.0 / 5`).
* **Reason:** Context-relevant justification detailing what was achieved in the text.
* **Critic:** Constructive critique identifying what is missing, weak, or could be improved.
* **Quoted Evidence:** Exact verbatim textual citation from the submission.

### 5. Dual Alignment Analytics & Comparison Dashboard
* Visual side-by-side progress bars comparing Human vs. AI scores.
* Total score differences and agreement classification (**Strong Agreement**, **Moderate Agreement**, **Significant Divergence**).
* **Save & Done (Proceed to Dashboard)** and **View Previous Results** navigation buttons to ensure users never get stuck.
* Full evaluation history with JSON export.

### 6. Dual AI Execution Modes
* **Offline Engine (Built-in):** Evaluates submissions locally with realistic evidence-grounded scoring without requiring an API key.
* **Live Gemini Mode:** Enter a Google Gemini API key in **Settings** to run real-time inference via Gemini 2.5 Flash.

---

## 📁 Repository Structure

```
.
├── index.html                  # HTML entry point
├── package.json                # Project dependencies & scripts
├── vite.config.js              # Vite bundler configuration
├── dist/                       # Production build output
├── src/
│   ├── App.jsx                 # Main application controller & router
│   ├── main.jsx                # React DOM mount point
│   ├── index.css               # Clean white design system (ui-ux-pro-max)
│   ├── components/
│   │   ├── AccessGate.jsx           # Passkey authentication gate
│   │   ├── Header.jsx               # Navigation bar & live status
│   │   ├── DocumentReaderSheet.jsx  # A4 paper reading sheet with line numbers
│   │   ├── MicroExplainer.jsx       # 3-step animated tutorial walkthrough
│   │   └── ScoreInput.jsx           # Tactile 0.5-step pills & score steppers
│   ├── pages/
│   │   ├── HomePage.jsx             # Dashboard & quick upload
│   │   ├── NewEvaluationPage.jsx    # Document setup & AI rubric calibration
│   │   ├── EvaluatePage.jsx         # Examiner scoring, AI critique & split view
│   │   ├── HistoryPage.jsx          # Records, search filters & JSON export
│   │   └── SettingsPage.jsx         # Gemini API key & model settings
│   ├── data/
│   │   └── sampleEvaluations.js     # Preloaded realistic evaluation cases
│   └── utils/
│       ├── gemini.js                # Gemini REST API & local evaluation generator
│       ├── scoring.js               # Dual alignment mathematics & error tracking
│       ├── storage.js               # Browser-local state persistence
│       └── textParser.js            # File parsing & word count utilities
├── test_deep_verification.py       # Automated Playwright 9-suite E2E verification test
└── test_react_app.py               # E2E flow test
```

---

## 🧪 Automated End-to-End Verification

The complete workflow has been verified with an automated Playwright test suite covering all 13 steps:
```bash
python test_react_app.py
```

### Verified Test Steps:
1. Passkey authentication gate validation.
2. Home dashboard & animated micro-explainer render.
3. Skip guide dismissal and state persistence.
4. Document text submission and title auto-suggestion.
5. AI rubric generation and customization.
6. Examiner A4 paper sheet rendering with line numbers.
7. Side-by-side split view mode.
8. Human scoring input and validation (0.5 increment checks).
9. AI evaluation trigger.
10. AI Suggested Mark, Reason, and Critic rendering.
11. Save & Done navigation back to Dashboard.
12. History inspection and record persistence.

---

## 🛠️ Technology Stack
* **Framework:** React 18.3
* **Build Tool:** Vite 5.4
* **UI Design System:** Modern SaaS Clean White (inspired by `ui-ux-pro-max`)
* **Icons:** Lucide React
* **AI Engine:** Google Gemini 2.5 Flash REST API + Local Grounding Fallback
