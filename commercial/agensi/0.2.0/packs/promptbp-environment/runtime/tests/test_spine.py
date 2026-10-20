import copy
import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from promptbp.__main__ import main
from promptbp.spine import compile_intent, record_outcome
from promptbp.validation import validate_document


def request(**changes):
    return {"intent": "Inspect the repository and establish verified state.", "action": "inspect",
            "source": "github", "target": "dburt-proex/Runwall", "surface": "auto",
            "constraints": ["Read only."], "evidence_required": ["repository head", "open PRs"],
            "acceptance_criteria": ["head verified", "PRs verified"], **changes}


def context(**changes):
    return {"authority": "read_only", "authority_ref": "operator instruction 001",
            "scope": ["dburt-proex/Runwall"], "available_surfaces": ["chat", "work", "codex", "plugin", "automation"],
            "available_sources": ["conversation", "github", "workspace", "plugin"], **changes}


def observation(**changes):
    return {"status": "completed", "reported_by": "executor receipt 001", "evidence": ["local evidence receipt 001"],
            "checks": [{"name": "head verified", "status": "passed"},
                       {"name": "PRs verified", "status": "passed"}], **changes}


class SpineTests(unittest.TestCase):
    def test_read_only_github_handoff_reuses_seven_layers(self):
        result = compile_intent(request(), context())
        self.assertEqual("work", result["route"]["surface"])
        self.assertEqual("ALLOW", result["gate"]["status"])
        self.assertEqual("not_started", result["receipt"]["execution_status"])
        self.assertEqual([], result["receipt"]["evidence"])
        self.assertTrue(result["directive"]["handoff_ready"])
        self.assertEqual([], validate_document(result["directive"]))
        self.assertEqual(request()["intent"], result["directive"]["prompt"]["objective"])

    def test_route_matrix_for_all_five_surfaces(self):
        cases = [
            ({"source": "conversation", "action": "analyze"}, {}, "chat", "ALLOW"),
            ({}, {}, "work", "ALLOW"),
            ({"source": "workspace"}, {}, "codex", "ALLOW"),
            ({"source": "plugin", "plugin": "notion"}, {"available_plugins": ["notion"]}, "plugin", "ALLOW"),
            ({"action": "schedule", "schedule": "Every weekday at 09:00 America/Chicago"},
             {"authority": "local_write"}, "automation", "REVIEW"),
        ]
        for intent, operator, surface, gate in cases:
            with self.subTest(surface=surface):
                result = compile_intent(request(**intent), context(**operator))
                self.assertEqual(surface, result["route"]["surface"])
                self.assertEqual(gate, result["gate"]["status"])

    def test_explicit_surface_is_preserved(self):
        self.assertEqual("codex", compile_intent(request(surface="codex"), context())["route"]["surface"])

    def test_unavailable_route_and_source_do_not_fallback(self):
        for operator in (context(available_surfaces=["chat"]), context(available_sources=[])):
            result = compile_intent(request(), operator)
            self.assertEqual("work", result["route"]["surface"])
            self.assertEqual("REVIEW", result["gate"]["status"])
            self.assertFalse(result["directive"]["handoff_ready"])

    def test_plugin_requires_exact_availability_and_surface(self):
        for intent in (request(source="plugin"), request(source="plugin", plugin="unknown"),
                       request(source="plugin", surface="work"), request(plugin="notion", surface="chat")):
            with self.subTest(intent=intent):
                self.assertEqual("REVIEW", compile_intent(intent, context())["gate"]["status"])

    def test_automation_cannot_silently_create_a_schedule(self):
        for intent in (request(action="schedule"), request(surface="automation"),
                       request(action="schedule", surface="work", schedule="daily")):
            result = compile_intent(intent, context(authority="local_write"))
            self.assertEqual("REVIEW", result["gate"]["status"])
            self.assertFalse(result["directive"]["handoff_ready"])

    def test_target_scope_is_exact_not_a_prefix(self):
        for target in ("dburt-proex/Runwall-other", "dburt-proex/Runwall/../CASA"):
            result = compile_intent(request(target=target), context())
            self.assertEqual("HALT", result["gate"]["status"])
            self.assertIsNone(result["directive"])

    def test_request_cannot_self_grant_authority(self):
        result = compile_intent(request(authority="local_write"), context())
        self.assertEqual("REVIEW", result["gate"]["status"])
        self.assertFalse(result["receipt"]["compiled"])

    def test_local_write_requires_operator_authority_and_no_readonly_conflict(self):
        intent = request(intent="Fix the failing parser tests.", action="edit_local", source="workspace", file_count=2)
        self.assertEqual("HALT", compile_intent(intent, context())["gate"]["status"])
        operator = context(authority="local_write", reversible=True, rollback="restore the saved local patch")
        self.assertEqual("HALT", compile_intent(intent, operator)["gate"]["status"])
        intent["constraints"] = []
        self.assertEqual("ALLOW", compile_intent(intent, operator)["gate"]["status"])

    def test_unknown_large_or_irreversible_local_scope_requires_review(self):
        intent = request(intent="Fix failing tests.", action="edit_local", source="workspace", constraints=[])
        operator = context(authority="local_write", reversible=True, rollback="restore local patch")
        for change in ({}, {"file_count": 6}):
            self.assertEqual("REVIEW", compile_intent({**intent, **change}, operator)["gate"]["status"])
        self.assertEqual("REVIEW", compile_intent({**intent, "file_count": 1}, context(authority="local_write"))["gate"]["status"])

    def test_external_actions_never_automatically_allow(self):
        for action in ("external_write", "send", "publish", "deploy", "merge", "spend", "change_credentials",
                       "change_schema", "change_api", "change_architecture", "change_dependencies", "change_auth"):
            with self.subTest(action=action):
                self.assertEqual("HALT", compile_intent(request(action=action), context())["gate"]["status"])
                self.assertEqual("REVIEW", compile_intent(request(action=action), context(authority="local_write"))["gate"]["status"])

    def test_halt_actions_and_operator_prohibitions_never_emit_directive(self):
        for action in ("destructive", "reveal_secret", "bypass_security"):
            result = compile_intent(request(action=action), context(authority="local_write"))
            self.assertEqual("HALT", result["gate"]["status"])
            self.assertIsNone(result["directive"])
        self.assertEqual("HALT", compile_intent(request(), context(prohibited_actions=["inspect"]))["gate"]["status"])

    def test_conflicting_narrative_cannot_bypass_gate_with_inspect_label(self):
        result = compile_intent(request(intent="Inspect and merge the repository."), context())
        self.assertEqual("REVIEW", result["gate"]["status"])

    def test_missing_or_malformed_inputs_always_review(self):
        cases = [(None, context()), (request(), None), ({}, {}), (request(action="unknown"), context()),
                 (request(file_count=True), context()), (request(evidence_required=[]), context()),
                 (request(), context(authority_ref="")), (request(), context(available_sources="github")),
                 (request(), context(available_surfaces=[[]])), (request(source=[]), context())]
        for intent, operator in cases:
            with self.subTest(intent=intent, operator=operator):
                result = compile_intent(intent, operator)
                self.assertEqual("REVIEW", result["gate"]["status"])
                self.assertFalse(result["receipt"]["compiled"])

    def test_compilation_is_stable_and_input_mutation_is_isolated(self):
        intent, operator = request(), context()
        result = compile_intent(intent, operator)
        self.assertEqual(result, compile_intent(request(), context()))
        intent["target"] = "other"
        operator["scope"].append("other")
        self.assertEqual("dburt-proex/Runwall", result["directive"]["target"])
        self.assertEqual(["dburt-proex/Runwall"], result["context"]["scope"])

    def test_receipt_and_ledger_mark_execution_as_reported_not_verified(self):
        result = record_outcome(compile_intent(request(), context()), observation(lesson="Keep the source explicit."))
        self.assertEqual("reported_completed", result["receipt"]["execution_status"])
        self.assertEqual("not_verified_by_promptbp", result["receipt"]["evidence_verification"])
        self.assertEqual("Keep the source explicit.", result["evolution_entry"]["lesson"])

    def test_completion_requires_all_acceptance_checks_and_evidence(self):
        compiled = compile_intent(request(), context())
        cases = [observation(evidence=[]), observation(checks=[]),
                 observation(checks=[{"name": "head verified", "status": "passed"}]),
                 observation(checks=[{"name": "head verified", "status": "not_run"}]),
                 observation(checks=[{"name": "head verified", "status": "failed"}])]
        for outcome in cases:
            with self.subTest(outcome=outcome), self.assertRaises(ValueError):
                record_outcome(compiled, outcome)

    def test_review_or_halt_cannot_be_reported_completed(self):
        for compiled in (compile_intent(request(), context(available_surfaces=[])),
                         compile_intent(request(target="other"), context())):
            with self.assertRaises(ValueError):
                record_outcome(compiled, observation())
            blocked = record_outcome(compiled, observation(status="blocked", evidence=[], checks=[]))
            self.assertEqual("reported_blocked", blocked["receipt"]["execution_status"])

    def test_failed_execution_preserves_failed_or_unrun_checks(self):
        checks = [{"name": "head verified", "status": "failed"}, {"name": "PRs verified", "status": "not_run"}]
        result = record_outcome(compile_intent(request(), context()), observation(status="failed", checks=checks))
        self.assertEqual(checks, result["receipt"]["checks"])

    def test_tampered_directive_context_or_receipt_binding_is_rejected(self):
        compiled = compile_intent(request(), context())
        for field in ("directive", "context", "receipt"):
            changed = copy.deepcopy(compiled)
            if field == "receipt":
                changed[field]["gate"] = "REVIEW"
            else:
                changed[field]["authority"] = "local_write"
            with self.subTest(field=field), self.assertRaises(ValueError):
                record_outcome(changed, observation())

    def test_malformed_outcome_and_duplicate_check_names_fail(self):
        compiled = compile_intent(request(), context())
        for outcome in (None, observation(status="planned"), observation(reported_by=""),
                        observation(evidence="unverified"), observation(checks=[{}]),
                        observation(checks=[{"name": "x", "status": "passed"}] * 2)):
            with self.subTest(outcome=outcome), self.assertRaises(ValueError):
                record_outcome(compiled, outcome)

    def test_receipt_metadata_cannot_promote_reported_evidence_or_approval(self):
        for change in ({"evidence_verification": "verified_by_promptbp"},
                       {"execution_status": "completed"}, {"owner_approved": True},
                       {"evidence": ["invented reference"]}):
            changed = compile_intent(request(), context())
            changed["receipt"].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                record_outcome(changed, observation())


class SpineCLITests(unittest.TestCase):
    def call(self, args):
        output = StringIO()
        with redirect_stdout(output):
            code = main(args)
        return code, json.loads(output.getvalue())

    def test_compile_exit_codes_and_receipt_round_trip(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            intent, operator, compiled, observed = (root / name for name in ("intent.json", "context.json", "compiled.json", "observed.json"))
            operator.write_text(json.dumps(context()))
            for value, expected in ((request(), 0), (request(surface="plugin"), 2), (request(target="other"), 3)):
                intent.write_text(json.dumps(value))
                code, result = self.call(["compile", str(intent), "--context", str(operator)])
                self.assertEqual(expected, code)
                self.assertEqual("not_started", result["receipt"]["execution_status"])
                if code == 0:
                    compiled.write_text(json.dumps(result))
            observed.write_text(json.dumps(observation()))
            code, result = self.call(["receipt", str(compiled), str(observed)])
            self.assertEqual(0, code)
            self.assertEqual("reported_completed", result["receipt"]["execution_status"])

    def test_bad_json_missing_files_duplicate_keys_and_nonfinite_values_fail_closed(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            bad, operator = root / "bad.json", root / "context.json"
            operator.write_text(json.dumps(context()))
            for text in ("{", '{"intent":"private-marker","intent":"override"}', '{"intent":NaN}'):
                bad.write_text(text)
                code, result = self.call(["compile", str(bad), "--context", str(operator)])
                self.assertEqual(2, code)
                self.assertEqual("REVIEW", result["gate"]["status"])
                self.assertNotIn("private-marker", json.dumps(result))
            code, result = self.call(["compile", str(root / "missing.json"), "--context", str(operator)])
            self.assertEqual(2, code)
            self.assertFalse(result["receipt"]["compiled"])


def capability(identifier, kind, provides, tasks=("all",), surfaces=("chat", "work", "codex"), **extra):
    return {"id": identifier, "kind": kind, "provides": provides, "task_classes": list(tasks),
            "surfaces": list(surfaces), "ref": "test-fixture:" + identifier, **extra}


def registry():
    return [
        capability("daily-model", "model", ["reasoning"], thinking=["medium", "high"]),
        capability("repository-tools", "tool", ["repository_read", "file_read", "file_write", "test_run", "change_gate"], tasks=("repository_review", "software_change")),
        capability("web-tools", "tool", ["current_web", "company_verification", "job_research"], tasks=("buyer_research", "resume")),
        capability("documents", "tool", ["document_generation"], tasks=("resume",)),
        capability("repository-context", "context", ["repository_context", "instruction_context"], tasks=("repository_review", "software_change")),
        capability("buyer-context", "context", ["offer_context", "outreach_context"], tasks=("buyer_research",)),
        capability("resume-context", "context", ["employment_evidence", "job_posting"], tasks=("resume",)),
        capability("repository-skill", "skill", ["repository_review", "software_change"], tasks=("repository_review", "software_change")),
        capability("buyer-skill", "skill", ["buyer_qualification"], tasks=("buyer_research",)),
        capability("resume-skill", "skill", ["resume_writing"], tasks=("resume",)),
    ]


class EnvironmentTests(unittest.TestCase):
    def compile(self, **changes):
        return compile_intent(request(**changes), context(capability_registry=registry(), available_sources=["github", "workspace", "conversation", "web"]))

    def test_repo_manifest_preserves_context_authority_and_proposed_settings(self):
        result = self.compile(task_class="repository_review")
        env = result["environment"]
        self.assertEqual("ALLOW", result["gate"]["status"])
        self.assertFalse(env["applied"])
        self.assertEqual({"id": "daily-model", "thinking": "high", "ref": "test-fixture:daily-model"}, env["model"])
        self.assertEqual("read_only", env["authority"]["mode"])
        self.assertEqual(request()["acceptance_criteria"], env["acceptance_criteria"])
        self.assertEqual(env, result["directive"]["environment"])
        self.assertEqual("daily-model", result["directive"]["prompt"]["metadata"]["model_target"])

    def test_buyer_and_resume_profiles_exclude_repository_infrastructure(self):
        for kind, source in (("buyer_research", "web"), ("resume", "conversation")):
            result = self.compile(task_class=kind, source=source, action="analyze", intent="Produce the bounded requested artifact.")
            self.assertEqual("ALLOW", result["gate"]["status"])
            self.assertEqual("chat", result["route"]["surface"])
            selected = [item["id"] for key in ("tools", "contexts", "skills") for item in result["environment"][key]]
            self.assertFalse(any("repository" in name for name in selected))

    def test_missing_registry_or_required_capability_requires_review(self):
        result = compile_intent(request(task_class="repository_review"), context())
        self.assertEqual("REVIEW", result["gate"]["status"])
        for removed in ("daily-model", "repository-tools", "repository-context", "repository-skill"):
            operator = context(capability_registry=[item for item in registry() if item["id"] != removed])
            self.assertEqual("REVIEW", compile_intent(request(task_class="repository_review"), operator)["gate"]["status"])

    def test_requested_model_or_thinking_has_no_silent_substitution(self):
        for changes in ({"model": "unavailable"}, {"thinking": "unavailable"}):
            result = self.compile(**changes)
            self.assertEqual("REVIEW", result["gate"]["status"])
            self.assertIsNone(result["environment"]["model"])

    def test_minimum_cover_can_choose_one_tool_over_two_earlier_tools(self):
        pool = registry()
        pool.insert(1, capability("read-only", "tool", ["repository_read"], tasks=("software_change",)))
        pool.insert(2, capability("files-only", "tool", ["file_read", "file_write"], tasks=("software_change",)))
        operator = context(authority="local_write", reversible=True, rollback="restore saved patch", capability_registry=pool)
        result = compile_intent(request(task_class="software_change", action="edit_local", source="workspace", constraints=[],
                                        file_count=2, intent="Fix failing tests."), operator)
        self.assertEqual("ALLOW", result["gate"]["status"])
        self.assertEqual(["repository-tools"], [item["id"] for item in result["environment"]["tools"]])

    def test_registry_metadata_never_grants_write_authority(self):
        result = self.compile(task_class="software_change", action="edit_local", source="workspace", file_count=1, constraints=[])
        self.assertEqual("HALT", result["gate"]["status"])
        self.assertIsNone(result["directive"])

    def test_registry_rejects_design_scores_duplicates_and_malformed_values(self):
        for pool in ([{"average_score": 92}], registry() + [registry()[0]], [{}], [None], "design catalog"):
            result = compile_intent(request(), context(capability_registry=pool))
            self.assertEqual("REVIEW", result["gate"]["status"])

    def test_unknown_class_or_inconsistent_task_metadata_requires_review(self):
        for changes in ({"task_class": "invented"}, {"task_class": "buyer_research"},
                        {"task_class": "software_change"}, {"task_class": "repository_review", "source": "conversation"}):
            self.assertEqual("REVIEW", self.compile(**changes)["gate"]["status"])

    def test_environment_is_bound_to_completion_receipt(self):
        result = self.compile()
        self.assertEqual("reported_completed", record_outcome(result, observation())["receipt"]["execution_status"])
        result["environment"]["model"]["id"] = "tampered"
        with self.assertRaises(ValueError):
            record_outcome(result, observation())

    def test_registry_scoping_and_explicit_surface_are_respected(self):
        pool = registry()
        pool[0]["surfaces"] = ["chat"]
        self.assertEqual("REVIEW", compile_intent(request(), context(capability_registry=pool))["gate"]["status"])
        result = self.compile(surface="codex")
        self.assertEqual("codex", result["environment"]["surface"])

    def test_cli_compiles_environment_and_records_bound_outcome(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            intent, operator, compiled, observed = (root / name for name in ("intent.json", "context.json", "compiled.json", "observed.json"))
            intent.write_text(json.dumps(request(task_class="repository_review")))
            operator.write_text(json.dumps(context(capability_registry=registry())))
            output = StringIO()
            with redirect_stdout(output):
                code = main(["compile", str(intent), "--context", str(operator)])
            self.assertEqual(0, code)
            compiled.write_text(output.getvalue())
            self.assertIn("environment", json.loads(output.getvalue()))
            observed.write_text(json.dumps(observation()))
            with redirect_stdout(StringIO()):
                self.assertEqual(0, main(["receipt", str(compiled), str(observed)]))

    def test_automation_manifest_never_bypasses_schedule_review(self):
        pool = [capability("scheduler-model", "model", ["reasoning"], surfaces=("automation",), thinking=["medium"]),
                capability("scheduler-prepare", "tool", ["schedule_prepare"], surfaces=("automation",)),
                capability("task-context", "context", ["task_context"], surfaces=("automation",))]
        result = compile_intent(request(action="schedule", source="conversation", schedule="weekday mornings", task_class="automation"),
                                context(authority="local_write", capability_registry=pool))
        self.assertEqual("REVIEW", result["gate"]["status"])
        self.assertEqual([], result["environment"]["issues"])
        self.assertFalse(result["environment"]["handoff_ready"])

    def test_general_and_plugin_manifests_require_only_relevant_roles(self):
        for surface, source in (("chat", "conversation"), ("plugin", "plugin")):
            pool = [capability("generic-model", "model", ["reasoning"], surfaces=(surface,), thinking=["medium"]),
                    capability("task-context", "context", ["task_context"], surfaces=(surface,))]
            changes = {"task_class": "general", "source": source, "surface": surface, "action": "analyze"}
            if surface == "plugin":
                changes["plugin"] = "example-plugin"
                pool.append(capability("plugin-read", "tool", ["plugin_access"], surfaces=(surface,)))
            operator = context(capability_registry=pool, available_plugins=["example-plugin"])
            result = compile_intent(request(**changes), operator)
            self.assertEqual("ALLOW", result["gate"]["status"])
            self.assertEqual(surface, result["environment"]["surface"])
            self.assertEqual(0 if surface == "chat" else 1, len(result["environment"]["tools"]))

    def test_excessive_eligible_inventory_requires_narrowing_before_selection(self):
        pool = registry() + [capability("extra-" + str(i), "tool", ["repository_read"]) for i in range(20)]
        result = compile_intent(request(), context(capability_registry=pool))
        self.assertEqual("REVIEW", result["gate"]["status"])
        self.assertTrue(any("sixteen" in reason for reason in result["gate"]["reasons"]))

    def test_general_retains_source_route_and_requires_source_access(self):
        for source, surface, role in (("github", "work", "repository_read"), ("workspace", "codex", "file_read"), ("web", "chat", "current_web")):
            pool = [capability("generic-model", "model", ["reasoning"], thinking=["medium"]),
                    capability("task-context", "context", ["task_context"])]
            operator = context(capability_registry=pool, available_sources=[source])
            intent = request(task_class="general", source=source, action="analyze")
            result = compile_intent(intent, operator)
            self.assertEqual(surface, result["route"]["surface"])
            self.assertEqual("REVIEW", result["gate"]["status"])
            pool.append(capability("source-reader", "tool", [role]))
            self.assertEqual("ALLOW", compile_intent(intent, operator)["gate"]["status"])


if __name__ == "__main__":
    unittest.main()
