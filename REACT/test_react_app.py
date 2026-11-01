import time
from playwright.sync_api import sync_playwright

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
APP_URL = "http://localhost:5173"

def run_test():
    print(">>> Starting React app E2E verification via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True
        )
        page = browser.new_page()

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

        # 3. Verify Home Page
        print("3. Verifying Home page navigation...")
        page.wait_for_selector("text=Start a New Evaluation")
        page.wait_for_selector("text=Recent Evaluations")

        # 4. Test Fast-Track Text Submission
        print("4. Entering sample submission text...")
        textarea = page.locator('textarea[placeholder*="paste submission text"]')
        textarea.fill("# Real-Time API Gateway Security\n\nWe implemented token bucket rate limiting on Redis clusters, handling 50,000 req/sec with 2ms latency.")
        page.click('button:has-text("Proceed to Evaluation Setup")')
        page.wait_for_timeout(1000)

        # 5. Verify Setup Page & Suggested Title
        print("5. Verifying suggested title...")
        page.wait_for_selector("text=Submission Setup")
        title_val = page.input_value("#eval-title")
        print(f"   Suggested Title: {title_val}")
        assert "Real-Time API Gateway Security" in title_val

        # 6. Generate Rubric
        print("6. Generating evaluation rubric...")
        page.click('button:has-text("Analyze Submission with AI")')
        page.wait_for_selector("text=Review & Customize Rubric", timeout=10000)
        print("   Rubric generated successfully!")

        # 7. Approve Rubric
        print("7. Approving rubric and transitioning to scoring...")
        page.click('button:has-text("Approve Rubric & Begin Evaluation")')
        page.wait_for_timeout(1000)

        # 8. Human Scoring
        print("8. Entering human scores...")
        page.wait_for_selector("text=Human Scoring")
        score_inputs = page.locator('input[type="number"][step="0.5"]').all()
        print(f"   Found {len(score_inputs)} criteria to score.")
        for inp in score_inputs:
            inp.fill("4.5")
        page.click('button:has-text("Submit Human Scores")')
        page.wait_for_timeout(1000)

        # 9. AI Scoring
        print("9. Running AI evaluation...")
        page.wait_for_selector('button:has-text("Run AI Evaluation with Gemini")')
        page.click('button:has-text("Run AI Evaluation with Gemini")')
        page.wait_for_timeout(2000)

        # 10. Verify Comparison Dashboard
        print("10. Verifying Comparison Dashboard...")
        page.wait_for_selector("text=Comparison Dashboard: Human vs. AI")
        page.wait_for_selector("text=Human Score")
        page.wait_for_selector("text=AI Suggestion")
        page.wait_for_selector("text=Score Difference")

        # 11. Save & Done (Proceed to Dashboard)
        print("11. Clicking Save & Done (Proceed to Dashboard)...")
        page.click('button:has-text("Save & Done (Proceed to Dashboard)")')
        page.wait_for_timeout(1000)
        page.wait_for_selector("text=Recent Evaluations")

        # 12. Check History
        print("12. Checking Evaluation History...")
        page.click('button:has-text("History")')
        page.wait_for_timeout(1000)
        page.wait_for_selector("text=Real-Time API Gateway Security")

        print("\n>>> ALL 12 REACT WORKFLOW STEPS VERIFIED AND PASSED!")
        browser.close()

if __name__ == "__main__":
    run_test()
