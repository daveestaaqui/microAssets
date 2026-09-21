"""
Unit tests for interactive tool navigation flows (diagnostics.html & mycology-finder.html)
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTICS_PATH = ROOT / "tools" / "diagnostics.html"
FINDER_PATH = ROOT / "tools" / "mycology-finder.html"


class TestToolNavigation(unittest.TestCase):
    def setUp(self):
        self.assertTrue(DIAGNOSTICS_PATH.is_file(), "tools/diagnostics.html must exist")
        self.assertTrue(FINDER_PATH.is_file(), "tools/mycology-finder.html must exist")
        self.diag_html = DIAGNOSTICS_PATH.read_text(encoding="utf-8")
        self.finder_html = FINDER_PATH.read_text(encoding="utf-8")

    def test_diagnostics_step1_no_back_button(self):
        """Verify back button is hidden on step 1 both in initial markup and in JS logic."""
        # Initial markup check
        self.assertRegex(
            self.diag_html,
            r'<button[^>]*id="btnBack"[^>]*style="display:\s*none;"',
            "Initial HTML for btnBack must have display: none;"
        )
        # JS updateNavButtons check
        self.assertIn("btnBack.style.display = 'none';", self.diag_html,
                      "updateNavButtons must hide btnBack when currentStep === 1")

    def test_diagnostics_step3_back_handler(self):
        """Verify back button works on final part (step 3) to navigate back to step 2."""
        # Check btnBack click handler covers step 3
        self.assertRegex(
            self.diag_html,
            r'else\s+if\s*\(\s*currentStep\s*===\s*3\s*\)\s*\{\s*goToStep2\(\);',
            "btnBack click listener must call goToStep2() when currentStep === 3"
        )
        # Check goToStep2 hides diagResult and restores quiz step 2
        self.assertIn("diagResult.style.display = 'none';", self.diag_html)
        self.assertIn("renderStep2Options();", self.diag_html)

    def test_diagnostics_result_inpage_back_button(self):
        """Verify in-page back button exists inside diagnosis results for instant access."""
        self.assertIn('onclick="goToStep2()"', self.diag_html,
                      "Diagnostics results content must include direct 'goToStep2()' back button")

    def test_finder_step1_no_back_button(self):
        """Verify Step 1 of mycology-finder has no back button."""
        step1_match = re.search(r'<div[^>]*id="step1"[^>]*>(.*?)</div>\s*<!-- Step 2', self.finder_html, re.DOTALL)
        self.assertTrue(step1_match, "Step 1 container must be found")
        step1_content = step1_match.group(1)
        self.assertNotIn("btn-step-back", step1_content, "Step 1 must not contain a back button")

    def test_finder_steps_and_results_have_back_buttons(self):
        """Verify Step 2, Step 3, and Results have appropriate back buttons."""
        self.assertIn('onclick="prevStep(1)"', self.finder_html, "Step 2 must have back button to Step 1")
        self.assertIn('onclick="prevStep(2)"', self.finder_html, "Step 3 must have back button to Step 2")
        self.assertIn('onclick="prevStep(3)"', self.finder_html, "Results must have back button to quiz Step 3")
        self.assertIn('onclick="resetQuiz()"', self.finder_html, "Results must have retake quiz button")


if __name__ == '__main__':
    unittest.main()
