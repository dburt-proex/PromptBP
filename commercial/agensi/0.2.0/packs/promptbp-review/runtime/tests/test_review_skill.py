"""Exercise the local skill helper's handoff and target-preservation boundaries."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from promptbp.spine import record_outcome

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills" / "promptbp-review" / "scripts" / "prepare_review.py"
TARGET = "dburt-proex/PromptBP"


def operator(target=TARGET, source="github"):
    def capability(identifier, kind, roles, **extra):
        return {"id": identifier, "kind": kind, "provides": roles, "surfaces": ["codex"],
                "task_classes": ["repository_review"], "ref": "test-fixture:" + identifier, **extra}
    return {"authority": "read_only", "authority_ref": "test-fixture:owner-review",
            "scope": [target], "available_surfaces": ["codex"], "available_sources": [source],
            "capability_registry": [capability("declared-model", "model", ["reasoning"], thinking=["high"]),
                                    capability("repository-reads", "tool", ["repository_read", "file_read"]),
                                    capability("repository-context", "context", ["repository_context", "instruction_context"]),
                                    capability("review-instructions", "skill", ["repository_review"])]}


class ReviewSkillTests(unittest.TestCase):
    def prepare(self, directory, context=None, target=TARGET, source="github", output=None, extra=(), raw=None):
        context_path = Path(directory) / "operator.json"
        context_path.write_text(raw if raw is not None else json.dumps(context or operator()), encoding="utf-8")
        output = output or Path(directory) / "packet"
        process = subprocess.run([sys.executable, "-B", str(HELPER), "--target", target, "--source", source,
                                  "--context", str(context_path), "--output", str(output), *extra],
                                 cwd=ROOT, capture_output=True, text=True, timeout=15)
        return process, output

    def test_shipped_helper_creates_read_only_unapplied_environment_handoff(self):
        with TemporaryDirectory() as directory:
            process, output = self.prepare(directory, extra=("--model", "declared-model", "--thinking", "high"))
            self.assertEqual(0, process.returncode, process.stderr)
            compiled = json.loads((output / "compiled.json").read_text())
            self.assertEqual("ALLOW", compiled["gate"]["status"])
            self.assertEqual("codex", compiled["route"]["surface"])
            self.assertEqual("read_only", compiled["directive"]["authority"])
            self.assertEqual("declared-model", compiled["environment"]["model"]["id"])
            self.assertFalse(compiled["environment"]["applied"])
            self.assertEqual("not_started", compiled["receipt"]["execution_status"])
            self.assertEqual([], compiled["receipt"]["evidence"])

    def test_missing_model_blocks_and_can_bind_an_explicit_blocked_report(self):
        with TemporaryDirectory() as directory:
            context = operator()
            context["capability_registry"] = context["capability_registry"][1:]
            process, output = self.prepare(directory, context=context)
            self.assertEqual(2, process.returncode)
            compiled = json.loads((output / "compiled.json").read_text())
            self.assertEqual("REVIEW", compiled["gate"]["status"])
            self.assertFalse(compiled["environment"]["handoff_ready"])
            result = record_outcome(compiled, {"status": "blocked", "reported_by": "test-fixture:host",
                                              "evidence": ["test-fixture:missing-model"], "checks": []})
            self.assertEqual("reported_blocked", result["receipt"]["execution_status"])
            with self.assertRaises(ValueError):
                record_outcome(compiled, {"status": "completed", "reported_by": "test-fixture:host",
                                          "evidence": ["test-fixture:missing-model"], "checks": []})

    def test_out_of_scope_target_retains_halt_without_a_directive(self):
        with TemporaryDirectory() as directory:
            process, output = self.prepare(directory, target="dburt-proex/Other")
            self.assertEqual(3, process.returncode)
            compiled = json.loads((output / "compiled.json").read_text())
            self.assertEqual("HALT", compiled["gate"]["status"])
            self.assertIsNone(compiled["directive"])

    def test_unknown_requested_model_is_not_substituted(self):
        with TemporaryDirectory() as directory:
            process, output = self.prepare(directory, extra=("--model", "unavailable-model"))
            self.assertEqual(2, process.returncode)
            self.assertIsNone(json.loads((output / "compiled.json").read_text())["environment"]["model"])

    def test_write_authority_is_not_silently_downgraded_or_accepted(self):
        with TemporaryDirectory() as directory:
            context = operator()
            context["authority"] = "local_write"
            process, output = self.prepare(directory, context=context)
            self.assertEqual(2, process.returncode)
            self.assertFalse(output.exists())
            self.assertEqual("local_write", json.loads((Path(directory) / "operator.json").read_text())["authority"])

    def test_invalid_operator_json_does_not_echo_input_or_create_a_packet(self):
        with TemporaryDirectory() as directory:
            process, output = self.prepare(directory, raw='{"authority":"read_only","authority":"untrusted-private-value"}')
            self.assertEqual(2, process.returncode)
            self.assertNotIn("untrusted-private-value", process.stdout + process.stderr)
            self.assertFalse(output.exists())

    def test_packet_write_failure_returns_review_without_a_ready_compilation(self):
        main = runpy.run_path(str(HELPER))["main"]
        write_text = Path.write_text
        names = ("intent.json", "operator-context.json", "compiled.json")
        for failed_index, failed_name in enumerate(names):
            with self.subTest(failed_write=failed_name), TemporaryDirectory() as directory:
                workspace = Path(directory) / "workspace"
                workspace.mkdir()
                marker = workspace / "keep.txt"
                marker.write_text("owner content", encoding="utf-8")
                context_path = Path(directory) / "operator.json"
                context_path.write_text(json.dumps(operator(str(workspace), "workspace")), encoding="utf-8")
                original_context = context_path.read_bytes()
                output = Path(directory) / "packet"

                def fail_packet_write(path, data, *args, **kwargs):
                    if path == output / failed_name:
                        raise OSError("private-write-failure-detail")
                    return write_text(path, data, *args, **kwargs)

                captured = StringIO()
                with patch.object(Path, "write_text", fail_packet_write), redirect_stdout(captured):
                    code = main(["--target", str(workspace), "--source", "workspace",
                                 "--context", str(context_path), "--output", str(output)])
                result = json.loads(captured.getvalue())
                self.assertEqual(2, code)
                self.assertEqual("REVIEW", result["gate"])
                self.assertIsNone(result["packet"])
                self.assertNotIn("private-write-failure-detail", captured.getvalue())
                self.assertFalse((output / "compiled.json").exists())
                self.assertEqual(set(names[:failed_index]), {path.name for path in output.iterdir()})
                self.assertEqual(original_context, context_path.read_bytes())
                self.assertEqual("owner content", marker.read_text(encoding="utf-8"))

    def test_output_cannot_overwrite_existing_files_or_enter_the_compiler_checkout(self):
        with TemporaryDirectory() as directory:
            marker = Path(directory) / "keep.txt"
            marker.write_text("owner content")
            process, _ = self.prepare(directory, output=Path(directory))
            self.assertEqual(2, process.returncode)
            self.assertEqual("owner content", marker.read_text())
            repository_output = ROOT / ("review-packet-" + Path(directory).name)
            process, _ = self.prepare(directory, output=repository_output)
            self.assertEqual(2, process.returncode)
            self.assertFalse(repository_output.exists())

    def test_workspace_review_outputs_stay_outside_the_review_target(self):
        with TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            workspace.mkdir()
            marker = workspace / "keep.txt"
            marker.write_text("owner content")
            context = operator(str(workspace), "workspace")
            process, output = self.prepare(directory, context=context, target=str(workspace), source="workspace")
            self.assertEqual(0, process.returncode, process.stderr)
            self.assertEqual("owner content", marker.read_text())
            self.assertFalse(json.loads((output / "compiled.json").read_text())["environment"]["applied"])
            process, output = self.prepare(directory, context=context, target=str(workspace), source="workspace", output=workspace / "packet")
            self.assertEqual(2, process.returncode)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
