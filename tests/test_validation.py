import copy
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import yaml

from promptbp.validation import validate_document, validate_file
from promptbp.__main__ import main


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
        output = StringIO()
        with redirect_stdout(output):
            code = main(["demo"])
        self.assertEqual(0, code)
        self.assertIn("Sample: VALID", output.getvalue())
        self.assertIn("Missing objective: INVALID", output.getvalue())


if __name__ == "__main__":
    unittest.main()
