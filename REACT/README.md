# EvalLens — React Application

A simple, fast web app to compare human grading with AI grading.

---

## Quick Start (3 Steps)

1. Open this folder in your terminal:
   ```bash
   cd REACT
   ```

2. Install packages:
   ```bash
   npm install
   ```

3. Start the app:
   ```bash
   npm run dev
   ```

Open `http://localhost:5173` in your browser.

---

## How to Use

### 1. Log In
- Enter the prototype passkey: `evallens2026`
- Click **Access Workspace**.

### 2. Start an Evaluation
- On the **Home** page, drop any text or code file, or paste your text.
- Check the word counter (must be 5,000 words or fewer).
- Click **Proceed to Evaluation Setup**.

### 3. Build or Generate Your Rubric
- Click **Analyze Submission with AI** to generate criteria automatically, or click **Create Rubric Manually**.
- Edit any criterion name, description, or marks.
- Click **Approve Rubric & Begin Evaluation**.

### 4. Grade as a Human
- Enter your scores (using `0.5` steps like 3.5, 4.0, 4.5).
- Add optional comments.
- Click **Submit Human Scores**.

### 5. Run AI Grading
- Click **Run AI Evaluation with Gemini**.
- The AI grades each criterion independently and quotes real text evidence from the submission.

### 6. Compare Scores
- Look at the **Comparison Dashboard**:
  - Side-by-side bars for Human vs. AI.
  - Overall difference (**MAE %**).
  - Agreement status (Strong, Moderate, or Divergent).
  - Quoted evidence for each grade.
- Click **Mark Evaluation as Completed & Lock** to save it as read-only.

---

## Optional: Live Google Gemini API Key

EvalLens includes a built-in offline engine so you can test everything immediately without any API key.

If you want live AI responses from Google:
1. Go to **Settings**.
2. Paste your Gemini API key.
3. Click **Test Key**, then click **Save Configuration**.

Your key stays inside your browser only. It is never sent to any other server.

---

## Build for Production

To create a static production build:
```bash
npm run build
npm run preview
```
The compiled files will be ready in `dist/`.
