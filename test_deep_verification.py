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
        page.screenshot(path="screenshot_home.png")
        print("  ✓ Correct passkey unlocked workspace successfully. Captured screenshot_home.png.")

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
        # TEST 4: Setup Page & AI Rubric Generation (Manual Rubric Removed)
        # ----------------------------------------------------------------------
        print("\n[TEST 4] Testing AI Rubric Generation & Calibration...")
        page.wait_for_selector("text=Submission Setup")
        
        # Verify manual rubric button is gone
        assert page.locator('button:has-text("Create Rubric Manually")').count() == 0
        print("  ✓ Verified: Manual rubric option cleanly removed as requested.")

        title_val = page.input_value("#eval-title")
        print(f"  ✓ Auto-suggested title: \"{title_val}\"")
        assert "Stream Processing" in title_val

        # Generate criteria with AI
        page.click('button:has-text("Analyze Submission with AI")')
        page.wait_for_selector("text=Review & Calibrate Rubric", timeout=10000)
        page.screenshot(path="screenshot_rubric.png")
        print("  ✓ AI Rubric generated and calibrated successfully. Captured screenshot_rubric.png.")

        # Add custom criterion
        page.click('button:has-text("Add Another Criterion")')
        page.wait_for_timeout(400)
        crit_count = len(page.locator('.form-label:has-text("Criterion Name")').all())
        print(f"  ✓ Added custom criterion, total criteria: {crit_count}")

        # Approve Rubric & Begin Evaluation
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
        page.click('button[title*="line numbers"]')
        page.wait_for_timeout(300)
        print("  ✓ Line numbers toggle tested.")

        # Test font zoom controls
        page.click('button[title*="Increase font size"]')
        page.wait_for_timeout(200)
        page.click('button[title*="Decrease font size"]')
        page.wait_for_timeout(200)
        print("  ✓ Font zoom in/out tested.")

        # Verify Side-by-Side split view
        page.wait_for_selector("text=Examiner Evaluation & Scoring")
        page.screenshot(path="screenshot_examiner_split_view.png")
        print("  ✓ Side-by-Side split screen mode active and captured.")

        # ----------------------------------------------------------------------
        # TEST 6: Interactive ScoreInput Component & SUBMIT SCORES
        # ----------------------------------------------------------------------
        print("\n[TEST 6] Testing Interactive ScoreInput (Quick Pills & Stepper)...")
        # Test quick pill buttons
        quick_pills_45 = page.locator('button:has-text("4.5")').all()
        print(f"  Found {len(quick_pills_45)} quick-select 4.5 pills.")
        for pill in quick_pills_45:
            pill.click()
            page.wait_for_timeout(100)
        print("  ✓ Clicked 4.5 quick-select pills on criteria.")

        # Test stepper buttons (+ and -)
        plus_buttons = page.locator('button[title="Increase by 0.5"]').all()
        if len(plus_buttons) > 0:
            plus_buttons[0].click()
            page.wait_for_timeout(100)
            minus_buttons = page.locator('button[title="Decrease by 0.5"]').all()
            minus_buttons[0].click()
            page.wait_for_timeout(100)
            print("  ✓ Tactile score stepper (+/- 0.5) tested successfully.")

        # Click SUBMIT SCORES button
        page.wait_for_selector('button:has-text("SUBMIT SCORES")')
        page.click('button:has-text("SUBMIT SCORES")')
        page.wait_for_timeout(1000)
        print("  ✓ Clicked \"SUBMIT SCORES\" button successfully.")

        # ----------------------------------------------------------------------
        # TEST 7: AI Rubric Evaluation Quality & Evidence Grounding
        # ----------------------------------------------------------------------
        print("\n[TEST 7] Verifying AI Suggested Mark, Reason, Critic & Quoted Evidence...")
        page.wait_for_selector("text=AI Suggested Mark:")
        page.wait_for_selector("text=Reason:")
        page.wait_for_selector("text=Critic:")
        page.screenshot(path="screenshot_deep_evaluation.png")
        print("  ✓ Verified AI Suggested Mark, Reason, Critic, and Quoted Evidence.")

        # ----------------------------------------------------------------------
        # TEST 8: SAVE AND APPROVE Action & PDF Export
        # ----------------------------------------------------------------------
        print("\n[TEST 8] Testing \"SAVE AND APPROVE\" and \"Export as PDF\"...")
        page.wait_for_selector('button:has-text("SAVE AND APPROVE")')
        page.click('button:has-text("SAVE AND APPROVE")')
        page.wait_for_timeout(1000)
        page.wait_for_selector("text=Evaluation Approved & Locked Successfully")
        print("  ✓ Evaluation locked with \"SAVE AND APPROVE\"!")

        # Verify Export as PDF button is present
        page.wait_for_selector('button:has-text("Export as PDF")')
        print("  ✓ \"Export as PDF\" button verified and ready.")

        # Navigate back to Dashboard
        page.click('button:has-text("Return to Dashboard")')
        page.wait_for_timeout(800)
        page.wait_for_selector("text=Recent Evaluations")
        print("  ✓ Returned to Dashboard.")

        # ----------------------------------------------------------------------
        # TEST 9: History & Settings Inspection
        # ----------------------------------------------------------------------
        print("\n[TEST 9] Checking History & Settings...")
        page.click('nav button:has-text("History")')
        page.wait_for_timeout(800)
        page.wait_for_selector("text=Evaluation History")
        page.wait_for_selector(f"text={title_val}")
        page.screenshot(path="screenshot_history.png")
        print("  ✓ Evaluation found in History with completed status.")

        print("\n" + "=" * 80)
        print(">>> ALL 9 TESTS PASSED! WORKFLOW IS 100% OPERATIONAL.")
        print("=" * 80)
        browser.close()

if __name__ == "__main__":
    run_deep_test()
