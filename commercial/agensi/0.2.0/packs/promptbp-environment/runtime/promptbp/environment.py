"""Compile a temporary task environment from operator-declared capabilities.

Selection is deterministic, not a prediction of model quality or a runtime setup.
"""

from itertools import combinations


PROFILES = {
    "repository_review": {"surface": "work", "thinking": "high", "tool": ["repository_read"],
                          "context": ["repository_context", "instruction_context"], "skill": ["repository_review"]},
    "software_change": {"surface": "codex", "thinking": "high", "tool": ["file_read", "file_write", "test_run", "change_gate"],
                        "context": ["repository_context", "instruction_context"], "skill": ["software_change"]},
    "buyer_research": {"surface": "chat", "thinking": "high", "tool": ["current_web", "company_verification"],
                       "context": ["offer_context", "outreach_context"], "skill": ["buyer_qualification"]},
    "resume": {"surface": "chat", "thinking": "medium", "tool": ["document_generation", "job_research"],
               "context": ["employment_evidence", "job_posting"], "skill": ["resume_writing"]},
    "automation": {"surface": "automation", "thinking": "medium", "tool": ["schedule_prepare"],
                   "context": ["task_context"], "skill": []},
    "general": {"surface": "chat", "thinking": "medium", "tool": [], "context": ["task_context"], "skill": []},
}


def task_class(request):
    if "task_class" in request:
        return request["task_class"]
    if request.get("action") == "schedule":
        return "automation"
    if request.get("action") == "edit_local":
        return "software_change"
    if request.get("source") in {"github", "workspace"}:
        return "repository_review"
    return "general"


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 8192


def _list(value, nonempty=True):
    return isinstance(value, list) and len(value) <= 64 and (bool(value) or not nonempty) and all(_text(x) for x in value)


def _cover(candidates, roles):
    if not roles:
        return []
    needed = set(roles)
    for count in range(1, min(len(needed), len(candidates)) + 1):
        for group in combinations(candidates, count):
            if needed.issubset(set().union(*(set(item["provides"]) for item in group))):
                return [{"id": item["id"], "ref": item["ref"],
                         "selected_roles": sorted(needed.intersection(item["provides"]))} for item in group]
    return None


def compile_environment(request, context, route):
    """Return a manifest and REVIEW issues; availability is operator asserted."""
    kind = task_class(request)
    result = {"schema_version": "environment-0.1", "task_class": kind, "surface": route["surface"],
              "applied": False, "availability_basis": "operator_registry", "issues": [],
              "selection_rule": "minimum capability count per kind; registry order breaks ties"}
    issues = result["issues"]
    if not isinstance(kind, str) or kind not in PROFILES:
        issues.append("unknown task class; select a documented bounded profile")
        return result
    profile = PROFILES[kind]
    registry = context.get("capability_registry")
    if not isinstance(registry, list) or not registry or len(registry) > 64:
        issues.append("environment compilation requires a bounded operator capability registry")
        return result
    fields = {"id", "kind", "provides", "surfaces", "task_classes", "ref", "thinking"}
    seen = set()
    for item in registry:
        if (not isinstance(item, dict) or set(item) - fields or not _text(item.get("id"))
                or item["id"] in seen or item.get("kind") not in ("model", "tool", "skill", "context")
                or not _text(item.get("ref")) or not _list(item.get("provides"))
                or not _list(item.get("surfaces")) or not _list(item.get("task_classes"))
                or any(x not in {"chat", "work", "codex", "plugin", "automation"} for x in item["surfaces"])
                or any(x not in set(PROFILES) | {"all"} for x in item["task_classes"])
                or (item["kind"] == "model" and not _list(item.get("thinking")))
                or (item["kind"] != "model" and "thinking" in item)):
            issues.append("invalid registry entry, reference, or duplicate capability id")
            return result
        seen.add(item["id"])
    if kind == "software_change" and request["action"] != "edit_local":
        issues.append("software_change requires an explicit edit_local action")
    if kind == "software_change" and request["source"] != "workspace":
        issues.append("software_change requires a scoped local workspace source")
    if kind == "buyer_research" and request["source"] != "web":
        issues.append("buyer_research requires an explicit current-web source")
    if kind == "repository_review" and request["source"] not in {"github", "workspace"}:
        issues.append("repository_review requires a repository or workspace source")
    if kind in {"buyer_research", "resume", "repository_review"} and request["action"] not in {"inspect", "analyze"}:
        issues.append("research/review profiles cannot authorize mutation or outreach")
    eligible = [item for item in registry if route["surface"] in item["surfaces"]
                and (kind in item["task_classes"] or "all" in item["task_classes"])]
    if len(eligible) > 16:
        issues.append("more than sixteen eligible capabilities; narrow the operator registry")
        return result
    thinking = request.get("thinking", profile["thinking"])
    model_id = request.get("model")
    models = [item for item in eligible if item["kind"] == "model"
              and thinking in item["thinking"] and (model_id is None or model_id == item["id"])]
    result["model"] = {"id": models[0]["id"], "thinking": thinking, "ref": models[0]["ref"]} if models else None
    if not models:
        issues.append("requested model/thinking is unavailable; no substitute or model switch")
    for capability_kind in ("tool", "skill", "context"):
        roles = list(profile[capability_kind])
        if capability_kind == "tool" and route["surface"] == "plugin":
            roles.append("plugin_access")
        if capability_kind == "tool" and request["source"] == "web" and "current_web" not in roles:
            roles.append("current_web")
        if capability_kind == "tool" and request["source"] == "github" and "repository_read" not in roles:
            roles.append("repository_read")
        if capability_kind == "tool" and request["source"] == "workspace" and "file_read" not in roles:
            roles.append("file_read")
        selected = _cover([item for item in eligible if item["kind"] == capability_kind], roles)
        result[capability_kind + "s"] = selected or []
        if selected is None:
            issues.append("missing required " + capability_kind + " roles: " + ", ".join(roles))
    result.update({"authority": {"mode": context["authority"], "ref": context["authority_ref"], "scope": context["scope"]},
                   "workspace": {"target": request["target"], "source": request["source"]},
                   "evidence_required": request["evidence_required"], "acceptance_criteria": request["acceptance_criteria"],
                   "constraints": request.get("constraints", []), "prohibited_actions": context.get("prohibited_actions", []),
                   "stop_conditions": ["Stop on REVIEW or HALT.", "Stop when required capabilities or evidence are unavailable.",
                                       "Stop before an action expands operator scope or authority."],
                   "receipt_required": ["facts", "changes", "evidence", "checks", "blockers", "gate", "next_action"]})
    return result
