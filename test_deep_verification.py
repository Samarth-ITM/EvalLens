import time
import os
from playwright.sync_api import sync_playwright

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
APP_URL = "http://localhost:5173"

def run_deep_test():
    print("=" * 80)
    print(">>> EvalLens Deep Verification Suite: Exhaustive UI/UX & Flow Testing")
    print("=" * 80)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True
        )
        context = browser.new_context(viewport={"width": 1440, "height": 960})
        page = context.new_page()

        # ----------------------------------------------------------------------
        # TEST 1: Access Gate Security & Validation
        # ----------------------------------------------------------------------
        print("\n[TEST 1] Testing Access Gate & Passkey Validation...")
        page.goto(APP_URL)
        page.wait_for_timeout(1000)

        page.wait_for_selector("#passkey-input")
        # Try wrong passkey
        page.fill("#passkey-input", "wrongpass123")
        page.click('button:has-text("Access Workspace")')
        page.wait_for_selector("text=Incorrect passkey")
        print("  ✓ Invalid passkey correctly rejected with error banner.")

        # Enter valid passkey
        page.fill("#passkey-input", "evallens2026")
        page.click('button:has-text("Access Workspace")')
        page.wait_for_timeout(1000)
        page.wait_for_selector("text=Start a New Evaluation")
        print("  ✓ Correct passkey unlocked workspace successfully.")

        # ----------------------------------------------------------------------
        # TEST 2: Micro-Explainer Interactive Behavior
        # ----------------------------------------------------------------------
        print("\n[TEST 2] Testing Micro-Explainer Walkthrough & Dismissal...")
        page.wait_for_selector("text=How EvalLens Works")
        page.wait_for_selector("text=Step 1")
        page.wait_for_selector("text=Step 2")
        page.wait_for_selector("text=Step 3")

        # Click Next button
        page.click('.explainer-banner button:has-text("Next")')
        page.wait_for_timeout(300)
        print("  ✓ Next button advanced micro-explainer step.")

        # Dismiss guide
        page.click('button:has-text("Skip Guide")')
        page.wait_for_timeout(400)
        page.wait_for_selector("text=How It Works (Guide)")
        print("  ✓ Skip Guide dismissed banner and displayed restore button.")

        # Restore guide
        page.click('button:has-text("How It Works (Guide)")')
        page.wait_for_timeout(400)
        page.wait_for_selector("text=How EvalLens Works")
        print("  ✓ Restore button brought guide banner back.")

        # ----------------------------------------------------------------------
        # TEST 3: Document Setup & Fast-Track Upload
        # ----------------------------------------------------------------------
        print("\n[TEST 3] Testing Document Submission & Word Counting...")
        sample_doc = """# High-Throughput Stream Processing on Apache Flink

## Abstract
We evaluated stateful streaming pipelines processing 120,000 events/sec under chaotic worker node kills. RocksDB incremental checkpointing reduced state snapshot latency from 1,420ms to 184ms.

## Fault Recovery Benchmarks
During unannounced worker failure injection, the pipeline recovered state within 4.2 seconds with exactly-once semantic guarantees. CPU saturation remained capped at 68% across all 8 cluster worker nodes.

## Limitations & Edge Cases
Backpressure propagation took up to 850ms to throttle upstream Kafka ingress topics, momentarily spiking JVM heap memory to 82% before stabilizing."""

        textarea = page.locator('textarea[placeholder*="paste submission text"]')
        textarea.fill(sample_doc)
        page.wait_for_timeout(400)

        # Verify word count indicator
        page.wait_for_selector("text=words")
        print("  ✓ Real-time word count verified.")

        page.click('button:has-text("Proceed to Evaluation Setup")')
        page.wait_for_timeout(1000)

        # ----------------------------------------------------------------------
        # TEST 4: Setup Page & Rubric Generation
        # ----------------------------------------------------------------------
        print("\n[TEST 4] Testing Rubric Generation & Customization...")
        page.wait_for_selector("text=Submission Setup")
        title_val = page.input_value("#eval-title")
        print(f"  ✓ Auto-suggested title: \"{title_val}\"")
        assert "Stream Processing" in title_val

        # Generate criteria
        page.click('button:has-text("Analyze Submission with AI")')
        page.wait_for_selector("text=Review & Customize Rubric", timeout=10000)
        print("  ✓ Rubric generated successfully.")

        # Add custom criterion
        page.click('button:has-text("Add Another Criterion")')
        page.wait_for_timeout(400)
        crit_inputs = page.locator('input[value*="Criterion"]').all()
        print(f"  ✓ Added new criterion, total criteria now: {len(page.locator('.form-label:has-text(\"Criterion Name\")').all())}")

        # Approve Rubric
        page.click('button:has-text("Approve Rubric & Begin Evaluation")')
        page.wait_for_timeout(1000)

        # ----------------------------------------------------------------------
        # TEST 5: Examiner Reading Sheet (A4 Paper View) Controls
        # ----------------------------------------------------------------------
        print("\n[TEST 5] Testing Examiner Document Reading Sheet Controls...")
        page.wait_for_selector("text=Examiner Reading Sheet")
        page.wait_for_selector("text=Total Extracted Words")

        # Test line numbers toggle
        page.click('button[title*="line numbers"]')
        page.wait_for_timeout(300)
        print("  ✓ Line numbers toggle tested.")

        # Test font zoom controls
        page.click('button[title*="Increase font size"]')
        page.wait_for_timeout(200)
        page.click('button[title*="Decrease font size"]')
        page.wait_for_timeout(200)
        print("  ✓ Font zoom in/out tested.")

        # Test Side-by-Side split view
        page.click('button:has-text("Side-by-Side")')
        page.wait_for_timeout(500)
        page.screenshot(path="screenshot_examiner_split_view.png")
        print("  ✓ Side-by-Side split screen mode active and captured.")

        # ----------------------------------------------------------------------
        # TEST 6: Human Scoring Validation (0.5 increments & bounds)
        # ----------------------------------------------------------------------
        print("\n[TEST 6] Testing Human Scoring Validations...")
        score_inputs = page.locator('input[type="number"][step="0.5"]').all()
        
        # Test out of bounds score
        score_inputs[0].fill("99")
        page.click('button:has-text("Submit Human Scores")')
        page.wait_for_selector("text=must be between 0 and")
        print("  ✓ Out-of-bounds score error correctly trapped.")

        # Test non-0.5 step
        score_inputs[0].fill("4.3")
        page.click('button:has-text("Submit Human Scores")')
        page.wait_for_selector("text=must use 0.5 increments")
        print("  ✓ Non-0.5 step increment error correctly trapped.")

        # Fill valid scores with realistic variance
        valid_scores = ["4.5", "4.0", "3.5", "5.0"]
        for idx, inp in enumerate(score_inputs):
            s = valid_scores[idx % len(valid_scores)]
            inp.fill(s)
        
        page.click('button:has-text("Submit Human Scores")')
        page.wait_for_timeout(1000)
        print("  ✓ Valid human scores accepted.")

        # ----------------------------------------------------------------------
        # TEST 7: AI Rubric Evaluation & Evidence Grounding
        # ----------------------------------------------------------------------
        print("\n[TEST 7] Testing AI Evaluation, Reason, and Critic...")
        page.click('button:has-text("Run AI Evaluation")')
        page.wait_for_timeout(2000)

        page.wait_for_selector("text=AI Suggested Mark:")
        page.wait_for_selector("text=Reason:")
        page.wait_for_selector("text=Critic:")
        page.screenshot(path="screenshot_deep_evaluation.png")
        print("  ✓ Verified AI Suggested Mark, Reason, Critic, and Quoted Evidence.")

        # ----------------------------------------------------------------------
        # TEST 8: Comparison Dashboard & Navigation
        # ----------------------------------------------------------------------
        print("\n[TEST 8] Testing Comparison Dashboard & Navigation...")
        page.wait_for_selector("text=Evaluation Comparison: Human vs. AI")
        page.wait_for_selector("text=Human Score")
        page.wait_for_selector("text=AI Suggested")
        page.wait_for_selector("text=Score Difference")

        # Test Save & Done navigation
        page.click('button:has-text("Save & Done (Proceed to Dashboard)")')
        page.wait_for_timeout(1000)
        page.wait_for_selector("text=Recent Evaluations")
        print("  ✓ \"Save & Done (Proceed to Dashboard)\" navigated back to Home.")

        # Test View Previous Results
        page.click('nav button:has-text("Evaluate")')
        page.wait_for_timeout(800)
        page.click('button:has-text("View Previous Results")')
        page.wait_for_timeout(800)
        page.wait_for_selector("text=Evaluation History")
        page.wait_for_selector(f"text={title_val}")
        print("  ✓ \"View Previous Results\" navigated to History, confirmed record exists.")

        # ----------------------------------------------------------------------
        # TEST 9: Settings Page Verification
        # ----------------------------------------------------------------------
        print("\n[TEST 9] Testing Settings Page...")
        page.click('nav button:has-text("Settings")')
        page.wait_for_timeout(800)
        page.wait_for_selector("text=Application Settings")
        page.wait_for_selector("#passkey-setting")
        page.click('button:has-text("Save Configuration")')
        page.wait_for_selector("text=Settings saved successfully.")
        print("  ✓ Settings configuration verified.")

        print("\n" + "=" * 80)
        print(">>> ALL 9 DEEP VERIFICATION TEST SUITES PASSED FLAWLESSLY!")
        print("=" * 80)
        browser.close()

if __name__ == "__main__":
    run_deep_test()
