"""Offline reference state checker for the instruction blocks' full build path.

No model calls, tools, automatic retries, or external authorization. Capability
outputs and check results are caller reports, not independently verified facts.
The host must keep this object and the contract outside untrusted execution.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import yaml


TYPES = {"text": str, "list": list, "object": dict, "boolean": bool,
         "number": (int, float)}


def load_contract(path):
    """Read the single mesh_state_contract YAML fence from the template."""
    contracts = []
    for block in Path(path).read_text(encoding="utf-8").split("```yaml\n")[1:]:
        document = yaml.safe_load(block.split("```", 1)[0])
        if isinstance(document, dict) and "mesh_state_contract" in document:
            contracts.append(document["mesh_state_contract"])
    if len(contracts) != 1:
        raise ValueError("expected exactly one mesh_state_contract")
    return contracts[0]


class MeshState:
    """Single-writer result namespaces with transitive invalidation.

    inputs_for() supplies an optimistic concurrency token; submit() rejects old
    tokens. snapshot() is a detached view. Neither hashes nor tokens authenticate
    a caller. This reference checker supports the declared full build DAG only.
    """

    def __init__(self, contract, *, authority, acceptance_criteria):
        self._contract = deepcopy(contract)
        capabilities = self._contract.get("capabilities", {})
        if not isinstance(capabilities, dict) or not capabilities:
            raise ValueError("missing capability contracts")
        seen = set()
        # YAML insertion order is the declared topological order.
        for name, spec in capabilities.items():
            dependencies = spec.get("depends_on")
            fields = spec.get("fields")
            if (not isinstance(dependencies, list) or not set(dependencies) <= seen
                    or len(set(dependencies)) != len(dependencies)
                    or not isinstance(fields, dict) or not fields
                    or any(kind not in TYPES for kind in fields.values())):
                raise ValueError(f"invalid dependencies or fields for {name}")
            seen.add(name)
        thresholds = self._contract.get("score_thresholds", {})
        expected = {"correctness", "completeness", "utility", "risk", "token_efficiency", "confidence"}
        if (set(thresholds) != expected
                or any(type(value) not in (int, float) or not 0 <= value <= 100
                       for value in thresholds.values())):
            raise ValueError("missing or invalid score thresholds")
        if (not isinstance(authority, dict) or not authority
                or not isinstance(acceptance_criteria, list) or not acceptance_criteria
                or any(not isinstance(item, str) or not item.strip() for item in acceptance_criteria)
                or len(set(acceptance_criteria)) != len(acceptance_criteria)):
            raise ValueError("authority and unique acceptance criteria are required host inputs")
        self._authority = deepcopy(authority)
        self._criteria = list(acceptance_criteria)
        self._results = {}
        self._history = []
        self._revision = 0
        self._conflict_review_required = False
        self._resolved_hard = None

    def _spec(self, name):
        if name not in self._contract["capabilities"]:
            raise ValueError(f"unknown capability: {name}")
        return self._contract["capabilities"][name]

    def inputs_for(self, name):
        """Return revisions of all required direct dependencies, or block."""
        dependencies = self._spec(name)["depends_on"]
        if any(dependency not in self._results for dependency in dependencies):
            raise ValueError(f"missing current dependencies for {name}")
        resolver = self._results.get("constraint_resolver")
        if name not in ("intent_router", "context_broker", "constraint_resolver") and resolver:
            if resolver["output"]["conflicts"]:
                raise ValueError("conflicting hard constraints require operator review")
        return {dependency: self._results[dependency]["revision"] for dependency in dependencies}

    def submit(self, name, output, inputs):
        """Atomically accept only a capability's own declared output payload."""
        spec = self._spec(name)
        if not isinstance(output, dict) or set(output) != set(spec["fields"]):
            raise ValueError(f"output fields do not match owner contract for {name}")
        for field, kind in spec["fields"].items():
            value = output[field]
            if (not isinstance(value, TYPES[kind])
                    or kind == "number" and type(value) is bool):
                raise ValueError(f"invalid type for {name}.{field}")
        if inputs != self.inputs_for(name):
            raise ValueError(f"stale input revisions for {name}")
        if name == "constraint_resolver":
            if self._conflict_review_required:
                raise ValueError("hard conflicts need host-recorded operator resolution")
            if self._resolved_hard is not None and not set(self._resolved_hard) <= set(output["hard"]):
                raise ValueError("resolver must preserve operator constraints")
        # Reject non-JSON data and NaN before any mutation; detach caller objects.
        encoded = json.dumps(output, sort_keys=True, ensure_ascii=True, allow_nan=False)
        detached = json.loads(encoded)
        self._retire(name, writer=name)
        if name == "constraint_resolver" and detached["conflicts"]:
            self._conflict_review_required = True
        self._results[name] = {"revision": self._revision, "inputs": deepcopy(inputs),
                               "sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
                               "output": detached}

    def _retire(self, name, *, writer):
        invalidated = {name}
        for candidate, candidate_spec in self._contract["capabilities"].items():
            if set(candidate_spec["depends_on"]) & invalidated:
                invalidated.add(candidate)
        retired = {key: self._results[key] for key in self._results if key in invalidated}
        self._revision += 1
        self._history.append({"revision": self._revision, "writer": writer,
                              "invalidated": sorted(retired), "retired": retired})
        self._results = {key: value for key, value in self._results.items() if key not in invalidated}

    def resolve_constraints(self, hard, *, review_ref):
        """Host-only record of operator-selected hard constraints, not model approval.

        The embedding host must verify review_ref and the actual operator decision.
        This offline checker does not authenticate review references.
        """
        if (not isinstance(hard, list) or any(not isinstance(item, str) or not item.strip() for item in hard)
                or not isinstance(review_ref, str) or not review_ref.strip()):
            raise ValueError("operator resolution needs hard constraints and review_ref")
        self._retire("constraint_resolver", writer="host:constraint_resolution")
        self._history[-1]["operator_resolution"] = {"hard": list(hard), "review_ref": review_ref}
        self._resolved_hard = list(hard)
        self._conflict_review_required = False

    def ready(self):
        """Check freshness and reported gates; never grant external permissions."""
        required = ("delivery_formatter", "validation_engine", "scoring_engine", "looper")
        if any(name not in self._results for name in required):
            return False
        resolver = self._results.get("constraint_resolver")
        if self._conflict_review_required or not resolver or resolver["output"]["conflicts"]:
            return False
        context = self._results.get("context_broker")
        if not context or context["output"]["context_gap"]:
            return False
        for name, result in self._results.items():
            if result["inputs"] != self.inputs_for(name):
                return False
        checks = self._results["validation_engine"]["output"]["checks"]
        if (not checks or any(not isinstance(check, dict) or set(check) != {"name", "status"}
                              or not isinstance(check["name"], str)
                              or check["status"] != "passed" for check in checks)):
            return False
        names = [check["name"] for check in checks]
        if len(set(names)) != len(names) or set(names) != set(self._criteria):
            return False
        scores = self._results["scoring_engine"]["output"]["scores"]
        thresholds = self._contract["score_thresholds"]
        if set(scores) != set(thresholds):
            return False
        for dimension, threshold in thresholds.items():
            score = scores[dimension]
            if type(score) not in (int, float) or not 0 <= score <= 100:
                return False
            if (dimension == "risk" and score > threshold
                    or dimension != "risk" and score < threshold):
                return False
        return self._results["looper"]["output"]["decision"] == "proceed"

    def snapshot(self):
        """Expose detached current/historical results and a host-derived handoff."""
        return deepcopy({"authority": self._authority, "acceptance_criteria": self._criteria,
                         "results": self._results, "history": self._history,
                         "handoff": {"status": "complete" if self.ready() else "needs_review",
                                     "external_actions_authorized": False}})
