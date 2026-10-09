# PromptBP

PromptBP vNext is a governed intent-to-directive compiler and execution router. Its smallest spine is **Intent -> Route -> Directive -> Gate -> Receipt**, with a JSON-ready evolution ledger interface. It reuses the seven-layer prompt structure and its offline validator. Routes target Chat, Work, Codex, plugins, and automations through manual handoff; the executor retains tool permissions and runtime enforcement.

The vNext compiler was merged in [PR #8](https://github.com/dburt-proex/PromptBP/pull/8), following the baseline repair in [PR #7](https://github.com/dburt-proex/PromptBP/pull/7). This repository supplies an offline compiler and manual handoff; no live host integration or deployment is included. The existing capability mesh and model-scoring proposals remain design assets.

## Install and verify

Requires Python 3.10+ and a checkout containing this increment. Use an isolated environment and the existing dependency declaration.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m promptbp validate schemas/prompt.sample.yaml
python -m promptbp demo
```

The commands report `VALID` for the included sample and `INVALID` when the demo removes its required objective. Validation checks document structure and nonempty fields; it does not score an LLM answer, enforce tool permissions, or establish output quality. The demo runs offline.

The package remains version `0.1.0`; the new handoff contract is `vnext-0.1`. The `1.0.0` label in legacy YAML versions that sample prompt.

## Run the vNext starter example

From the repository root, after the existing install step, run the shipped inputs:

```powershell
python -m promptbp compile examples/vnext/intent.json --context examples/vnext/operator-context.json
```

The command prints a JSON envelope with the intent, Work route, read-only directive, `ALLOW` gate, and compilation receipt. Expected exit code: `0`. The receipt stays `execution_status: not_started`, with empty `evidence` and `checks`; compilation performs no repository inspection or network call.

Both files are **illustrative only**. The operator context's authority reference and Work/GitHub availability are example declarations, not real approval or verified host capabilities. `ALLOW` applies to those declarations; it is not permission to execute the example. Before real work, copy the inputs outside the tracked examples and have the owner or trusted host supply actual authority, exact scope and verified availability. Recompile and honor REVIEW/HALT.

This starter uses the minimal spine without the optional task-environment stage. It selects no model, enables no tools, and records no execution outcome. See the later sections for environment manifests and receipts after actual manual execution.

## Compile a governed directive

Create `intent.json` (requested work):

```json
{
  "intent": "Inspect PromptBP and establish verified repository state.",
  "action": "inspect",
  "source": "github",
  "target": "dburt-proex/PromptBP",
  "surface": "auto",
  "constraints": ["Read only."],
  "evidence_required": ["repository head", "open PRs"],
  "acceptance_criteria": ["head verified", "PRs verified"]
}
```

Separately create `operator-context.json`. The operator or trusted host supplies this input; intent, retrieved content, and plugins cannot supply or expand it. The following is an illustrative availability declaration, not a connector health check:

```json
{
  "authority": "read_only",
  "authority_ref": "owner instruction for this inspection",
  "scope": ["dburt-proex/PromptBP"],
  "available_surfaces": ["work"],
  "available_sources": ["github"]
}
```

```powershell
python -m promptbp compile intent.json --context operator-context.json > compiled.json
```

The result contains the requested intent, selected route, a seven-layer directive, a gate with reasons, and a compilation receipt. Exit codes: `0` ALLOW, `2` REVIEW, `3` HALT. Compilation records `execution_status: not_started`; no task was executed. Copy an ALLOW directive into the selected host for manual execution. REVIEW directives are staged with `handoff_ready: false`; HALT emits no directive. The host must recheck scope, actual tool actions, and source availability.

Routing is deterministic from declared action/source, rather than unconstrained natural-language inference. `auto` selects Work for GitHub, Codex for workspace work, Chat for conversation analysis, a named plugin for plugin requests, or automation for an explicit schedule. An explicit surface is retained; an unavailable route never silently falls back.

The input contract rejects unknown fields and missing evidence/acceptance criteria. Source values are `conversation`, `github`, `workspace`, `plugin`, `web`; surfaces are `chat`, `work`, `codex`, `plugin`, `automation` or requested `auto`.

- `analyze` and `inspect` can ALLOW within exact scope and declared availability.
- `edit_local` requires `authority: local_write`, `file_count` at most five, and operator `reversible: true` plus a nonempty `rollback`. A read-only constraint wins over an edit request.
- External writes, sending, publishing, deployment, merging, spending, scheduling, and protected changes require REVIEW under local-write context. Read-only context cannot authorize these mutations and returns HALT. This spine has no approval override or dispatch implementation.
- Destructive actions, secret revelation, security bypasses, out-of-scope targets, and operator `prohibited_actions` return HALT.
- A plugin route needs `plugin` and a matching operator `available_plugins` identifier. Scheduling needs `action: schedule` and explicit `schedule` text; it remains staged for owner review. Schedule text is not validated or registered.

The full action/field vocabulary is in `promptbp/spine.py`. Extra narrative risk hints conservatively escalate to REVIEW; this small matcher is not a semantic safety classifier. Unrecognized conflicts or harmful instructions may require host review even when declared metadata qualifies for ALLOW. Context is operator-asserted, not authenticated by PromptBP.

## Bind the executor receipt and ledger entry

After manual execution, create `observation.json`. These are executor reports, not evidence independently verified by the compiler:

```json
{
  "status": "completed",
  "reported_by": "executor receipt reference",
  "evidence": ["reference to saved repository and PR inspection evidence"],
  "checks": [
    {"name": "head verified", "status": "passed"},
    {"name": "PRs verified", "status": "passed"}
  ],
  "lesson": "Keep the exact repository and authority reference in the handoff."
}
```

```powershell
python -m promptbp receipt compiled.json observation.json > receipt.json
```

The command returns a bound receipt and `evolution_entry` for a host-owned ledger. It performs no implicit append, storage, training, optimization, or policy change. Statuses are `reported_completed`, `reported_failed`, or `reported_blocked`; evidence verification stays `not_verified_by_promptbp`. Failed and blocked reports can include absent evidence or `failed`/`not_run` checks. Completion requires an unchanged current ALLOW compilation, evidence references, and a named passing check for every acceptance criterion. A valid receipt command exits `0` even when it records a failed outcome; invalid input or binding returns REVIEW and exit `2`.

SHA-256 binds the directive, operator context, route, and gate to the receipt. It detects accidental edits; it is not a signature or protection against an actor recomputing a hash. The host must authenticate authority, validate evidence, enforce actions, and own any durable decision/evolution ledger. PromptBP remains separate from CASA, Runwall, DiffWall, Operator Intelligence, and Daxxer.

## Compile a task environment

The new optional stage is **Intent -> Environment Compile -> Route -> Directive -> Gate -> Work -> Evidence -> Receipt**. Work and evidence verification remain host responsibilities. Intent classification determines the route and environment requirements together before any dispatch.

Use the repository skill in `skills/promptbp-environment/SKILL.md` to prepare intent and separate operator context. This is a reviewable repository asset; it has not been installed as a global skill or plugin. The existing compiler remains the intent router rather than introducing another agent platform.

Opt in by adding `task_class`, `model`, or `thinking` to the request, or `capability_registry` to operator context. Existing requests without these fields retain the original spine interface; they do not claim to have compiled a task environment. New task-environment requests with a missing registry return REVIEW.

| Task class | Default route / thinking | Required tool roles | Required context / skill roles |
|---|---|---|---|
| `repository_review` | Work (Codex for workspace) / high | repository_read | repository_context, instruction_context / repository_review |
| `software_change` | Codex / high | file_read, file_write, test_run, change_gate | repository_context, instruction_context / software_change |
| `buyer_research` | Chat / high | current_web, company_verification | offer_context, outreach_context / buyer_qualification |
| `resume` | Chat / medium | document_generation, job_research | employment_evidence, job_posting / resume_writing |
| `automation` | Automation / medium | schedule_prepare | task_context / none |
| `general` | Existing route / medium | source access as needed | task_context / none |

Buyer research requires `source: web`; repository review requires GitHub or workspace. Software change requires `action: edit_local` and `source: workspace`, with the existing authority/rollback/file-count gates. Research profiles cannot silently authorize outreach. Automation still requires owner review; it does not register a schedule.

`capability_registry` is a list of at most 64 operator-declared records. Each has `id`, `kind` (`model`, `tool`, `skill`, `context`), `provides` (role identifiers), `surfaces`, `task_classes` (documented classes or `all`), and `ref` (an actual host inventory/source reference). Models additionally need `thinking` (supported level strings). IDs must be unique. Legacy design entries with illustrative `average_score` values are not an executable capability inventory and are rejected.

Example record shape only; `example-model` is not a verified available provider model:

```json
{
  "id": "example-model",
  "kind": "model",
  "provides": ["reasoning"],
  "surfaces": ["work", "codex"],
  "task_classes": ["repository_review", "software_change"],
  "ref": "operator-provided host inventory reference",
  "thinking": ["medium", "high"]
}
```

Add corresponding tool, context, and specialized skill records for the task's required roles. Only eligible task/surface records are considered, with a maximum of sixteen eligible capabilities to bound selection work. Within each kind the compiler chooses the smallest set covering the required roles; registry order breaks equal-size ties. One tool providing several required roles can replace multiple narrower entries. Only the required roles appear in its `selected_roles`; actual permission narrowing still belongs to the host.

Models are selected in operator registry order, constrained by the requested thinking level and optional exact `model` ID. Defaults are profile preferences, not empirical success predictions. Unsupported model/thinking settings have no silent substitute. No cost, quality score, or probability of success is invented.

The result adds `environment` to the envelope and directive, including proposed model/thinking, mode, skills/tools/context references, authority, workspace, evidence, acceptance checks, constraints, stop conditions, and receipt requirements. `applied: false` means no model switch, tool activation, context loading, or permission change occurred. Missing roles produce REVIEW with exact role names. The unchanged environment is included in the receipt hash; outcome reporting cannot silently edit it or its authority. No environment is persisted globally, and an evolution entry does not update canonical routing rules.

## Try it in minutes

Copy the prompt into a language model. Compare its answer with the three checks below, then revise the weakest layer if a check fails.

```text
ROLE: Technical editor.
OBJECTIVE: Turn the raw note into one actionable issue summary.
INPUTS: Raw note: "The export button spins forever on an empty project. Tested in Chrome."
OUTPUT FORMAT: Exactly three lines: Symptom, Reproduction, Unknown.
PERFORMANCE RULES: Use only facts in the raw note. Do not invent a cause or claim a fix.
STYLE: Plain, concise language.
RECURSIVE CHECK: Before answering, confirm all three lines exist and each factual claim is grounded in the note.
```

Expected shape (wording may vary):

```text
Symptom: The export button spins indefinitely on an empty project in Chrome.
Reproduction: Exact steps were not supplied; observed on an empty project in Chrome.
Unknown: The cause and whether other browsers are affected are unknown.
```

Check: exactly three labeled lines; no invented cause or fix; uncertainty stated. This is a manual example, not a measured improvement or a deterministic model guarantee. For reusable fields, see [`schemas/prompt.sample.yaml`](schemas/prompt.sample.yaml) and [`framework.md`](framework.md).

## Current scope

The seven layers and sample schema remain usable as documentation and prompt templates. The validator checks the documented YAML structure; the vNext compiler uses it to check generated directives. The capability registry, composer, scoring engine, looper, and output evaluation runner remain design artifacts. Treat `evaluations/runner.md` command examples as proposed interfaces. No model invocation, platform adapter, autonomous execution loop, schedule registration, or durable ledger is implemented. Gate logic controls readiness of this compiler's handoff artifact; runtime controls belong to the host or separate tools.

## Repository guide

- [`framework.md`](framework.md) — the seven layers and their purpose.
- [`promptbp/spine.py`](promptbp/spine.py), [`tests/test_spine.py`](tests/test_spine.py) — vNext compiler, gates, receipt/ledger interface, and regression checks.
- [`promptbp/environment.py`](promptbp/environment.py), [`skills/promptbp-environment/SKILL.md`](skills/promptbp-environment/SKILL.md) — bounded environment compilation and the repository skill asset.
- [`examples.md`](examples.md), [`templates.md`](templates.md) — examples and a copyable template.
- [`schemas/prompt.schema.yaml`](schemas/prompt.schema.yaml), [`schemas/prompt.sample.yaml`](schemas/prompt.sample.yaml) — documented YAML structure and sample; `python -m promptbp validate` checks the seven required layers.
- [`docs/evaluation-layer.md`](docs/evaluation-layer.md) — manual review rubric.
- [`docs/architecture/capability-mesh-plan.md`](docs/architecture/capability-mesh-plan.md), [`registry/capabilities.yaml`](registry/capabilities.yaml), [`workflows/test-workflows.yaml`](workflows/test-workflows.yaml) — proposed capability model and sample workflows.
- [`evaluations/`](evaluations/) — proposed runner interface and sample fixtures.
- [`LICENSE`](LICENSE) — MIT reuse terms.

**Portfolio evidence:** [Systems & proof](https://drew-burt-portfolio.daxxer-os.chatgpt.site/systems)
