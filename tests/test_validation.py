import copy
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

from promptbp.validation import validate_document, validate_file


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "schemas" / "prompt.sample.yaml"


class StructuralValidationTests(unittest.TestCase):
    def test_shipped_sample_is_valid(self):
        self.assertEqual([], validate_file(SAMPLE))

    def test_missing_objective_fails(self):
        document = copy.deepcopy(yaml.safe_load(SAMPLE.read_text()))
        del document["prompt"]["objective"]
        self.assertIn("prompt.objective: expected nonempty text", validate_document(document))

    def test_bad_nested_types_fail(self):
        document = copy.deepcopy(yaml.safe_load(SAMPLE.read_text()))
        document["prompt"]["inputs"]["required"] = "raw text"
        document["prompt"]["grounding"]["citation_required"] = "false"
        errors = validate_document(document)
        self.assertTrue(any("inputs.required" in error for error in errors))
        self.assertTrue(any("grounding.citation_required" in error for error in errors))

    def test_malformed_yaml_fails_cleanly(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            path = Path(directory) / "bad.yaml"
            path.write_text("prompt: [unterminated\n")
            self.assertTrue(validate_file(path))

    def test_demo_exits_successfully_and_shows_control(self):
        result = subprocess.run(
            [sys.executable, "-m", "promptbp", "demo"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Sample: VALID", result.stdout)
        self.assertIn("Missing objective: INVALID", result.stdout)


if __name__ == "__main__":
    unittest.main()
