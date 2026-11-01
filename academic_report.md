# EvalLens: AI-Augmented Academic Evaluation & Dual Human-AI Grading Comparison System

**Project Report — Term Submission**

---

## Academic Submission Details

* **Student Name:** Samarth Navale
* **Roll Number:** 150096725148
* **Subject:** AI Prompt Engineering
* **Professor / Faculty Mentor:** Poonam Ma'am
* **Cohort:** Sam Altman
* **GitHub Repository:** [https://github.com/Samarth-ITM/EvalLens.git](https://github.com/Samarth-ITM/EvalLens.git)
* **Access Passkey:** `evallens2026`
* **Local Workspace URL:** `http://localhost:5173`

---

## 1. Executive Summary & Abstract

Traditional academic and technical grading often suffers from cognitive fatigue, inconsistent rubric enforcement, and subjectivity across human examiners. Simultaneously, fully autonomous AI grading systems lack human oversight, accountability, and the nuanced contextual intuition required for evaluating high-stakes academic papers, technical documentation, and complex source code.

**EvalLens** resolves this fundamental evaluation tension by introducing an **AI-Augmented Dual Evaluation & Comparative Analytics System**. Built as a clean, high-performance single-page web application, EvalLens facilitates a structured pair-evaluation workflow:
1. An academic examiner uploads or pastes student submissions across a wide range of formats (PDF, DOCX, Markdown, Code scripts, SQL, and plain text).
2. The system utilizes structured prompt engineering via Google Gemini to automatically extract contextual evaluation rubrics with explicit scoring guidance.
3. The examiner reads the submission on an interactive physical A4 reading sheet (complete with line numbers and font zoom controls) and assigns human marks using tactile 0.5-step quick-selection controls.
4. The AI engine runs an independent evaluation generating four transparent artifacts: **AI Suggested Mark**, **Contextual Reason**, **Constructive Critic**, and **Verbatim Quoted Evidence**.
5. The system computes real-time alignment metrics, visualizes score divergence, classifies consensus levels, and enables one-click academic PDF report generation.

---

## 2. Problem Statement & Educational Need

### 2.1 The Academic Evaluation Bottleneck
Evaluating technical reports, engineering submissions, and open-ended projects presents three recurring challenges:
* **Inter-Rater Inconsistency:** Examiners grading dozens of submissions exhibit score drift over time due to cognitive fatigue.
* **Lack of Grounded Feedback:** Providing detailed line-level critique with quoted evidence is time-prohibitive for large cohorts.
* **The "Black Box" AI Risk:** Fully automated AI graders often hallucinate generic compliments or award arbitrary scores (such as defaulting to 4.5/5.0) without rigorous justification or critical feedback.

### 2.2 System Objectives
* **Pair-Programming for Grading:** Place the human examiner in full control while giving them an objective, evidence-grounded AI co-evaluator.
* **Zero Cognitive Slop:** Eliminate dark, cluttered, confusing interfaces in favor of a pristine, accessible, distraction-free white theme compliant with WCAG AAA standards.
* **Auditability & Irreversibility:** Ensure evaluations can be formally submitted, approved, locked, and exported to PDF or JSON for institutional archives.

---

## 3. UI/UX Design Philosophy & Modern Clean Architecture

EvalLens is built on the principles of **clarity, speed, and tactile feedback**, following modern design guidelines:

### 3.1 Pristine White Minimalist Theme
* **Color Hierarchy:** Pure `#ffffff` card surfaces, soft `#f8fafc` workspace canvas, `#e2e8f0` structural hairline borders, and `#0284c7` deep cobalt accents.
* **High Contrast Typography:** Deep `#0f172a` primary text paired with clean slate `#475569` labels, ensuring maximum readability during prolonged grading sessions.
* **No "Dark AI Slop":** Rejected generic neon glow and dark gaming aesthetics in favor of professional academic editorial standards.

### 3.2 Key UI Components
* **Access Gate (`AccessGate.jsx`):** Secures the evaluation workspace with passkey validation (`evallens2026`) and instant error feedback.
* **Micro-Explainer Walkthrough (`MicroExplainer.jsx`):** An intuitive 3-step banner explaining the core workflow, complete with persistent skip preference and one-click restoration.
* **Examiner Document Reading Sheet (`DocumentReaderSheet.jsx`):** Emulates physical paper with selectable line numbering (`#`), font scaling (`- / +`), word count badges, and estimated reading time.
* **Tactile Score Selector (`ScoreInput.jsx`):** Replaced clunky raw number inputs with responsive 0.5-step quick-select pill buttons, stepper buttons, and instant performance grade indicators (`Outstanding A+`, `Proficient A`, `Acceptable B`, `Needs Improvement`).
* **Print-Ready Academic PDF Exporter (`@media print`):** Formats the evaluation sheet into an official academic grade sheet when printing or saving as PDF.

---

## 4. Screenshot Walkthrough of Core Workflows

### 4.1 Workspace Entry & Animated Walkthrough
The workspace is secured by passkey authentication. Upon entry, examiners can review or dismiss the 3-step micro-explainer and paste or upload submissions up to 5,000 words.

*(Figure 1: Workspace Home, Passkey Gate & Micro-Explainer)*

---

### 4.2 Dynamic Rubric Calibration & Review
AI analyzes the submission domain (e.g. Distributed Systems, Financial Engineering, Database Design) and generates calibrated criteria with custom scoring guidance. Examiners can adjust weights or add custom criteria before approving.

*(Figure 2: Review & Calibrate Rubric Screen)*

---

### 4.3 Side-by-Side Examiner Reading Sheet & Tactile Scoring
Examiners inspect the submission on the left reading sheet with line numbering enabled, while grading criteria on the right using 0.5-step tactile selector pills.

*(Figure 3: Side-by-Side Split View Grading Experience)*

---

### 4.4 Differentiated AI Evaluation & Critique
For every criterion, the AI provides an evidence-grounded assessment featuring four distinct fields: Suggested Mark, Contextual Reason, Constructive Critic, and Verbatim Quoted Evidence.

*(Figure 4: AI Suggested Mark, Reason, Critic & Quoted Evidence)*

---

### 4.5 Historical Archive & Academic Audit Trail
All evaluations are securely archived with title, word count, timestamps, criteria breakdown, and agreement ratings. Completed evaluations are locked against tampering and can be exported as PDF or JSON.

*(Figure 5: Evaluation History & Records Management)*

---

## 5. Prompt Engineering Methodology & AI Architecture

### 5.1 Contextual Rubric Generation Prompt
The rubric generation engine analyzes document structure, vocabulary, and objectives to formulate 3-4 domain-specific evaluation criteria:
* **System Prompt:** Instructs the LLM to act as a rigorous university assessment designer.
* **Output Format:** Strict JSON array containing `name`, `description`, `max_marks`, and `scoring_guidance`.
* **Zero Hallucination Anchor:** Scoring guidance explicitly references actual concepts identified in the submitted text rather than generic descriptors.

### 5.2 Evidence-Grounded Scoring & Critique Prompt
To eliminate generic feedback, the scoring prompt enforces strict constraints:
* **AI Suggested Mark:** Dynamic score calibration with natural variance (e.g., 3.5, 4.0, 4.5) reflecting observed strengths and shortcomings.
* **Reason:** Highlights specific technical achievements found in the document.
* **Critic:** Pinpoints missing baseline comparisons, unverified assumptions, or potential risks.
* **Quoted Evidence:** Mandates direct, verbatim excerpts (`"..."`) extracted from the text to validate each mark.

---

## 6. Mathematical Alignment & Dual Comparison Engine

EvalLens computes quantitative consensus metrics between human examiners and AI models:

* **Total Divergence Metric:**
  `Δ_total = |S_human - S_ai|`

* **Per-Criterion Delta:**
  `Δ_criterion = S_human,i - S_ai,i`

* **Holistic Agreement Rate:**
  `Agreement Rate = [ 1 - ( Σ |S_human,i - S_ai,i| / Σ M_i ) ] × 100%`

Where:
* **S_human:** Cumulative human examiner score across all criteria.
* **S_ai:** Cumulative AI-generated score across all criteria.
* **M_i:** Maximum marks allocated to criterion i.

### Agreement Classification Tiers:
* **Strong Agreement:** Total score variance ≤ 10%.
* **Moderate Agreement:** Total score variance between 11% and 20%.
* **Significant Divergence:** Total score variance > 20%, prompting the examiner to review specific criterion critiques before approving.

---

## 7. Automated Testing & Playwright Verification Results

The complete React application was verified using an automated Playwright end-to-end test suite (`test_deep_verification.py`), executing 9 comprehensive test suites:

| Test Suite | Target Feature | Verification Criteria | Status |
| :--- | :--- | :--- | :---: |
| **Test 1** | Access Gate Security | Invalid passkey rejected; valid passkey (`evallens2026`) grants entry | **PASSED** |
| **Test 2** | Micro-Explainer Guide | Multi-step navigation, skip preference persistence, and guide restore | **PASSED** |
| **Test 3** | Ingestion & Word Counter | Text parsing, real-time word counting, and title auto-suggestion | **PASSED** |
| **Test 4** | AI Rubric Calibration | Manual rubric removal verified; AI criteria generated and edited | **PASSED** |
| **Test 5** | Examiner Reading Sheet | A4 paper view, line numbers toggle, and font zoom (+/-) | **PASSED** |
| **Test 6** | Tactile Score Selector | 0.5-step quick pills, +/- steppers, and SUBMIT SCORES execution | **PASSED** |
| **Test 7** | Context AI Critique | Verification of AI Suggested Mark, Reason, Critic, and Quoted Evidence | **PASSED** |
| **Test 8** | Save & Approval Lock | SAVE AND APPROVE execution, status locking, and PDF export readiness | **PASSED** |
| **Test 9** | History & State Persistence | Archived record inspection and dashboard navigation | **PASSED** |

**Summary Result:** 9/9 Test Suites Passed (100% Success Rate).

---

## 8. Deployment & Examiner Verification Guide

### 8.1 Zero-Setup Clone & Run
Anyone cloning the repository can immediately build and run the application:

```bash
# 1. Clone repository
git clone https://github.com/Samarth-ITM/EvalLens.git
cd EvalLens

# 2. Install dependencies
npm install

# 3. Build production bundle (completes in < 1 second)
npm run build

# 4. Preview compiled application
npm run preview
```

### 8.2 Production Verification Details
* **Vite Bundler:** Built 1,591 modules in 605ms into optimized production bundle.
* **Zero Runtime Dependencies Outside npm:** Pure modern ECMAScript modules with Lucide React icons.
* **Offline Fallback:** Fully operational even when external Gemini API quota is offline.

---

## 9. Conclusion

EvalLens successfully bridges the divide between human pedagogical wisdom and artificial intelligence capabilities. By pairing an examiner-first physical reading interface with structured, evidence-grounded AI critiques, the platform reduces grading fatigue, enforces objective standards, and maintains transparent accountability in academic evaluations.

---

*Submitted by Samarth Navale (Roll No: 150096725148) for the course AI Prompt Engineering under the guidance of Professor Poonam Ma'am (Cohort: Sam Altman).*
