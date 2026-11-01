import time
import os
from playwright.sync_api import sync_playwright

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
APP_URL = "http://localhost:5173"

def run_test():
    print(">>> Starting Comprehensive React App UI/UX & Workflow E2E Verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True
        )
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        # 1. Visit App
        print("1. Loading app at http://localhost:5173...")
        page.goto(APP_URL)
        page.wait_for_timeout(1000)

        # 2. Passkey Gate
        print("2. Submitting passkey gate...")
        page.wait_for_selector("#passkey-input")
        page.fill("#passkey-input", "evallens2026")
        page.click('button:has-text("Access Workspace")')
        page.wait_for_timeout(1000)

        # 3. Verify Home Page & Micro-Explainer
        print("3. Verifying Home page & Animated Micro-Explainer...")
        page.wait_for_selector("text=How EvalLens Works")
        page.wait_for_selector("text=Skip Guide")
        page.screenshot(path="REACT/screenshot_home.png")
        print("   Captured REACT/screenshot_home.png")

        # Test Skip Guide
        page.click('button:has-text("Skip Guide")')
        page.wait_for_timeout(500)
        page.wait_for_selector("text=How It Works (Guide)")
        print("   Skip guide dismissed successfully and restore button is present.")

        # 4. Fast-Track Submission
        print("4. Submitting document content...")
        textarea = page.locator('textarea[placeholder*="paste submission text"]')
        textarea.fill("# Distributed Microservices Observability\n\nWe deployed OpenTelemetry collectors with Jaeger distributed tracing across 12 Kubernetes microservices. Latency spikes decreased by 34% under peak load.")
        page.click('button:has-text("Proceed to Evaluation Setup")')
        page.wait_for_timeout(1000)

        # 5. Verify Setup Page
        print("5. Verifying Setup page...")
        page.wait_for_selector("text=Submission Setup")
        title_val = page.input_value("#eval-title")
        print(f"   Suggested Title: {title_val}")
        assert "Distributed Microservices Observability" in title_val

        # 6. Generate Rubric
        print("6. Generating rubric...")
        page.click('button:has-text("Analyze Submission with AI")')
        page.wait_for_selector("text=Review & Customize Rubric", timeout=10000)
        page.screenshot(path="REACT/screenshot_rubric.png")
        print("   Captured REACT/screenshot_rubric.png (Rubric in pristine white UI)")

        # 7. Approve Rubric
        print("7. Approving rubric and transitioning to scoring...")
        page.click('button:has-text("Approve Rubric & Begin Evaluation")')
        page.wait_for_timeout(1000)

        # 8. Verify DocumentReaderSheet on Evaluate Page
        print("8. Verifying Examiner Reading Sheet...")
        page.wait_for_selector("text=Examiner Reading Sheet")
        page.wait_for_selector("text=Total Extracted Words")
        
        # Test split-screen toggle
        print("   Testing Side-by-Side Split View...")
        page.click('button:has-text("Side-by-Side")')
        page.wait_for_timeout(500)

        # 9. Enter Human Scores
        print("9. Entering human scores...")
        score_inputs = page.locator('input[type="number"][step="0.5"]').all()
        print(f"   Scoring {len(score_inputs)} criteria...")
        for idx, inp in enumerate(score_inputs):
            inp.fill("4.0" if idx % 2 == 0 else "4.5")
        
        page.click('button:has-text("Submit Human Scores")')
        page.wait_for_timeout(1000)

        # 10. Run AI Evaluation
        print("10. Triggering AI Evaluation...")
        page.click('button:has-text("Run AI Evaluation")')
        page.wait_for_timeout(2000)

        # 11. Verify AI Suggested Mark, Reason, Critic
        print("11. Verifying AI Suggested Mark, Reason, and Critic...")
        page.wait_for_selector("text=AI Suggested Mark:")
        page.wait_for_selector("text=Reason:")
        page.wait_for_selector("text=Critic:")
        page.screenshot(path="REACT/screenshot_evaluation.png")
        print("   Captured REACT/screenshot_evaluation.png (AI Suggested Mark, Reason, Critic)")

        # 12. Test Save & Done Navigation
        print("12. Testing Save & Done (Proceed to Dashboard)...")
        page.click('button:has-text("Save & Done (Proceed to Dashboard)")')
        page.wait_for_timeout(1000)
        page.wait_for_selector("text=Recent Evaluations")
        print("   Successfully navigated back to Dashboard!")

        # 13. Test View Previous Results
        print("13. Testing View Previous Results from Evaluate view...")
        page.click('nav button:has-text("Evaluate")')
        page.wait_for_timeout(800)
        page.click('button:has-text("View Previous Results")')
        page.wait_for_timeout(800)
        page.wait_for_selector("text=Evaluation History")
        page.screenshot(path="REACT/screenshot_history.png")
        print("   Captured REACT/screenshot_history.png")

        print("\n>>> ALL TEST PHASES PASSED WITH FLYING COLORS!")
        browser.close()

if __name__ == "__main__":
    run_test()
