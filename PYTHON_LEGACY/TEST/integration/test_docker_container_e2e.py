"""
Integration test for Docker container execution, live browser verification,
and volume persistence across container restarts.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FINAL_BUILD_DIR = BASE_DIR / "FINAL_BUILD"
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CONTAINER_URL = "http://localhost:8501"


def test_docker_container_workflow_and_persistence() -> None:
    """Execute complete browser workflow on the Docker container and test restart persistence."""
    print("\n>>> [Docker Test] Ensuring Docker container is running...")
    subprocess.run(["docker", "compose", "up", "-d"], cwd=str(FINAL_BUILD_DIR), check=True)
    time.sleep(3)

    try:
        print(">>> [Docker Test] Connecting to container at", CONTAINER_URL)

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

            # 1. Access Passkey Challenge
            page.goto(CONTAINER_URL)
            page.wait_for_timeout(1000)
            pwd_input = page.locator('input[type="password"]')
            assert pwd_input.is_visible(), "Access gate should be displayed on fresh container visit."
            print(">>> [Docker Test] Access gate challenged. Entering passkey...")
            pwd_input.fill("evallens2026")
            page.locator('button:has-text("Access Workspace")').click()
            page.wait_for_timeout(1500)

            page.wait_for_selector("section[data-testid=\"stSidebar\"]", timeout=15000)
            print(">>> [Docker Test] Successfully authenticated into Docker container workspace.")

            # 2. Navigate to New Evaluation
            page.locator("section[data-testid=\"stSidebar\"] label:has-text(\"New Evaluation\")").click()
            page.wait_for_selector("text=Evaluation Title*", timeout=15000)

            # Fill evaluation details
            page.locator('input[aria-label="Evaluation Title*"]').fill("Docker Container Production Evaluation")
            page.locator('textarea[aria-label="Evaluation Instructions (Optional)"]').fill(
                "Verify containerized execution, submission parsing, and rubric creation."
            )

            # Paste submission text
            sample_text = (
                "This is a verified production submission executing inside the isolated Docker container. "
                "The system evaluates architecture robustness, containerization, and data persistence."
            )
            page.locator('textarea[aria-label="Paste Submission Text"]').fill(sample_text)
            page.wait_for_timeout(500)

            # Choose manual rubric creation
            print(">>> [Docker Test] Submitting evaluation and creating rubric...")
            page.locator('button:has-text("Create Rubric Manually (Human-Only)")').click()
            page.wait_for_selector("text=Review & Edit Rubric", timeout=15000)
            page.wait_for_timeout(1000)

            # Approve Rubric
            print(">>> [Docker Test] Approving rubric...")
            page.locator('button:has-text("Approve Rubric")').click()
            page.wait_for_selector("text=Rubric Approved and Saved Successfully", timeout=15000)
            page.wait_for_timeout(1000)

            # Proceed to Score Evaluation
            print(">>> [Docker Test] Proceeding to score evaluation...")
            page.locator('button:has-text("Score Evaluation ➔")').click()
            page.wait_for_selector("text=Human Evaluation", timeout=15000)
            page.wait_for_timeout(1000)

            # Submit Human Evaluation
            print(">>> [Docker Test] Submitting human score...")
            page.locator('button:has-text("Submit Human Evaluation")').click()
            page.wait_for_selector("text=Human Evaluation Completed", timeout=15000)
            page.wait_for_timeout(1000)

            # Verify Comparison Dashboard renders
            print(">>> [Docker Test] Checking Comparison Dashboard...")
            body_text = page.locator("body").inner_text()
            assert "Human Evaluation Completed" in body_text
            assert "Comparison Dashboard" in body_text

            # Verify Evaluation History
            print(">>> [Docker Test] Checking Evaluation History...")
            page.locator("section[data-testid=\"stSidebar\"] label:has-text(\"Evaluation History\")").click()
            page.wait_for_selector("text=Evaluation History", timeout=15000)
            page.wait_for_timeout(1000)
            hist_text = page.locator("body").inner_text()
            assert "Docker Container Production Evaluation" in hist_text

            browser.close()

        # 3. Test Container Restart & Volume Persistence
        print(">>> [Docker Test] Restarting Docker container to test volume persistence...")
        res = subprocess.run(
            ["docker", "compose", "restart", "evallens"],
            cwd=str(FINAL_BUILD_DIR),
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0
        print(">>> [Docker Test] Waiting for container to become healthy again...")
        time.sleep(5)

        # 4. Re-open browser and verify evaluation survived restart
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=CHROME_PATH,
                headless=False,
                args=["--window-size=1280,950"],
            )
            context = browser.new_context(viewport={"width": 1280, "height": 950})
            page = context.new_page()

            print(">>> [Docker Test] Re-connecting after restart...")
            page.goto(CONTAINER_URL)
            page.wait_for_timeout(1000)

            # Re-authenticate
            pwd_input = page.locator('input[type="password"]')
            if pwd_input.is_visible():
                pwd_input.fill("evallens2026")
                page.locator('button:has-text("Access Workspace")').click()
                page.wait_for_timeout(1500)

            page.wait_for_selector("section[data-testid=\"stSidebar\"]", timeout=15000)
            page.locator("section[data-testid=\"stSidebar\"] label:has-text(\"Evaluation History\")").click()
            page.wait_for_selector("text=Evaluation History", timeout=15000)
            page.wait_for_timeout(1000)

            hist_text_after_restart = page.locator("body").inner_text()
            assert "Docker Container Production Evaluation" in hist_text_after_restart, (
                "Data in SQLite volume should persist across container restart!"
            )
            print(">>> [Docker Test] CONFIRMED: Evaluation persisted across container restart!")

            browser.close()

        print("\n>>> ALL DOCKER CONTAINER AND PERSISTENCE TESTS PASSED SUCCESSFULLY! <<<\n")

    finally:
        print(">>> [Docker Test] Tearing down container after test...")
        subprocess.run(["docker", "compose", "down"], cwd=str(FINAL_BUILD_DIR), check=True)


if __name__ == "__main__":
    test_docker_container_workflow_and_persistence()

