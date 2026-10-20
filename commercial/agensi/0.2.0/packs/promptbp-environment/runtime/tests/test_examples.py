"""Keep the shipped starter runnable without promoting it to execution evidence."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

from promptbp.validation import validate_document


ROOT = Path(__file__).resolve().parents[1]


class StarterExampleTests(unittest.TestCase):
    def test_shipped_starter_cli_compiles_without_execution_claims(self):
        process = subprocess.run(
            [sys.executable, "-B", "-m", "promptbp", "compile",
             "examples/vnext/intent.json", "--context", "examples/vnext/operator-context.json"],
            cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(0, process.returncode, process.stderr)
        compiled = json.loads(process.stdout)
        self.assertEqual("dburt-proex/PromptBP", compiled["intent"]["target"])
        self.assertEqual("work", compiled["route"]["surface"])
        self.assertEqual("ALLOW", compiled["gate"]["status"])
        self.assertEqual("read_only", compiled["directive"]["authority"])
        self.assertIn("ILLUSTRATIVE ONLY", compiled["directive"]["authority_ref"])
        self.assertTrue(any("ILLUSTRATIVE ONLY" in item for item in compiled["intent"]["constraints"]))
        self.assertEqual([], validate_document({"prompt": compiled["directive"]["prompt"]}))
        self.assertEqual("not_started", compiled["receipt"]["execution_status"])
        self.assertEqual([], compiled["receipt"]["evidence"])
        self.assertEqual([], compiled["receipt"]["checks"])
        self.assertEqual("not_verified_by_promptbp", compiled["receipt"]["evidence_verification"])
        self.assertNotIn("environment", compiled)


if __name__ == "__main__":
    unittest.main()
