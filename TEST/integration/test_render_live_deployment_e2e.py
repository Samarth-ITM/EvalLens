"""
End-to-End verification test for the live Render deployment of EvalLens.
Connects to https://evallens.onrender.com, tests real document upload (DOCX),
live Gemini AI criteria generation, human scoring, live Gemini AI evaluation,
comparison dashboard rendering, and history verification.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LIVE_RENDER_URL = "https://evallens.onrender.com"
SCREENSHOTS_DIR = BASE_DIR / "DOCS" / "screenshots" / "render_live"
FIXTURES_DIR = BASE_DIR / "TEST" / "fixtures"


def test_render_live_deployment_complete_workflow() -> None:
    """Execute complete end-to-end evaluation workflow on live Render deployment."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    test_docx = FIXTURES_DIR / "sample_report.docx"
    assert test_docx.exists(), f"Sample docx fixture missing: {test_docx}"

    print(f"\n>>> [Render Live Test] Connecting to live service at {LIVE_RENDER_URL}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=False,
            args=["--window-size=1280,950"],
        )
        context = browser.new_context(viewport={"width": 1280, "height": 950})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

        # 1. Access Passkey Gate
        print(">>> [Render Live Test] Loading landing page and verifying passkey gate...")
        page.goto(LIVE_RENDER_URL)
        page.wait_for_timeout(2000)

        # Handle Streamlit loading if initial wake-up takes a moment
        page.wait_for_selector('input[type="password"]', timeout=60000)
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_access_gate.png"))

        pwd_input = page.locator('input[type="password"]')
        assert pwd_input.is_visible(), "Passkey input must be visible on fresh visit."
        print(">>> [Render Live Test] Submitting access passkey...")
        pwd_input.fill("evallens2026")
        page.locator('button:has-text("Access Workspace")').click()
        page.wait_for_timeout(2000)

        page.wait_for_selector('section[data-testid="stSidebar"]', timeout=20000)
        print(">>> [Render Live Test] Successfully authenticated into Render workspace.")
        page.screenshot(path=str(SCREENSHOTS_DIR / "02_authenticated_home.png"))

        # 2. Navigate to New Evaluation
        print(">>> [Render Live Test] Navigating to New Evaluation page...")
        page.locator('section[data-testid="stSidebar"] label:has-text("New Evaluation")').click()
        page.wait_for_selector("text=Evaluation Title*", timeout=15000)
        page.wait_for_timeout(1000)

        # 3. Fill Evaluation Form & Upload Real DOCX File
        title = f"Live Render Verification: System Audit {int(time.time())}"
        print(f">>> [Render Live Test] Setting evaluation title: '{title}'...")
        page.locator('input[aria-label="Evaluation Title*"]').fill(title)
        page.locator('textarea[aria-label="Evaluation Instructions (Optional)"]').fill(
            "Perform rigorous evaluation of the submitted technical report focusing on methodology, results, and architecture."
        )

        print(">>> [Render Live Test] Uploading real DOCX document...")
        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(str(test_docx))
        page.wait_for_timeout(3000)

        # Verify parsed file appears
        body_text = page.locator("body").inner_text()
        assert "sample_report.docx" in body_text, "Uploaded file name should appear on page."
        assert "words" in body_text.lower(), "Extracted word count should appear."
        page.screenshot(path=str(SCREENSHOTS_DIR / "03_file_uploaded.png"))

        # 4. Request Gemini AI to Propose Evaluation Criteria
        print(">>> [Render Live Test] Triggering live Gemini criteria generation...")
        gemini_btn = page.locator('button:has-text("Analyze with Gemini AI")')
        assert gemini_btn.is_visible(), "AI criteria generation button must be visible."
        gemini_btn.click()

        print(">>> [Render Live Test] Waiting for Gemini API to return criteria...")
        page.wait_for_selector("text=Review & Edit Rubric", timeout=60000)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(SCREENSHOTS_DIR / "04_ai_criteria_generated.png"))
        print(">>> [Render Live Test] Gemini criteria generation succeeded!")

        # 5. Approve Rubric
        print(">>> [Render Live Test] Approving rubric...")
        approve_btn = page.locator('button:has-text("Approve Rubric")')
        approve_btn.click()
        page.wait_for_selector("text=Rubric Approved and Saved Successfully", timeout=15000)
        page.wait_for_timeout(1000)
        page.screenshot(path=str(SCREENSHOTS_DIR / "05_rubric_approved.png"))

        # 6. Proceed to Score Evaluation
        print(">>> [Render Live Test] Navigating to scoring page...")
        page.locator('button:has-text("Score Evaluation ➔")').click()
        page.wait_for_selector("text=Human Evaluation", timeout=15000)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(SCREENSHOTS_DIR / "06_scoring_page.png"))

        # 7. Submit Human Evaluation
        print(">>> [Render Live Test] Submitting human score...")
        submit_human_btn = page.locator('button:has-text("Submit Human Evaluation")')
        assert submit_human_btn.is_visible()
        submit_human_btn.click()
        page.wait_for_selector("text=Human Evaluation Completed", timeout=15000)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(SCREENSHOTS_DIR / "07_human_evaluation_completed.png"))

        # 8. Run Live AI Evaluation
        print(">>> [Render Live Test] Triggering live AI evaluation...")
        ai_eval_btn = page.locator('button:has-text("Run AI Evaluation with Gemini")')
        if ai_eval_btn.is_visible():
            ai_eval_btn.click()
            print(">>> [Render Live Test] Waiting for Gemini evaluation response...")
            page.wait_for_selector("text=AI Evaluation Completed", timeout=45000)
            page.wait_for_timeout(2000)
            page.screenshot(path=str(SCREENSHOTS_DIR / "08_ai_evaluation_completed.png"))
            print(">>> [Render Live Test] AI evaluation completed successfully!")

        # 9. Verify Comparison Dashboard
        print(">>> [Render Live Test] Checking comparison dashboard rendering...")
        body_text = page.locator("body").inner_text()
        assert "Comparison Dashboard" in body_text, "Comparison dashboard heading must render."
        assert "Score Alignment" in body_text or "Human Total" in body_text or "Points Variance" in body_text
        page.screenshot(path=str(SCREENSHOTS_DIR / "09_comparison_dashboard.png"))

        # 10. Check Evaluation History
        print(">>> [Render Live Test] Navigating to History page...")
        page.locator('section[data-testid="stSidebar"] label:has-text("Evaluation History")').click()
        page.wait_for_selector("text=Evaluation History", timeout=15000)
        page.wait_for_timeout(2000)
        page.screenshot(path=str(SCREENSHOTS_DIR / "10_evaluation_history.png"))

        history_text = page.locator("body").inner_text()
        assert title in history_text, f"Created evaluation '{title}' must appear in History list."
        print(">>> [Render Live Test] Evaluation verified in history!")

        context.close()
        browser.close()
        print(">>> [Render Live Test] ALL LIVE WORKFLOW TESTS PASSED!")


if __name__ == "__main__":
    test_render_live_deployment_complete_workflow()
