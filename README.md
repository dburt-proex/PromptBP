# PromptBP

PromptBP is a seven-layer prompt structure for making tasks, inputs, output shape, and review criteria explicit. This repository includes templates, illustrative YAML schemas and fixtures, and a proposed capability architecture. It does not currently ship a runnable execution engine or evaluation CLI.

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

The seven layers and sample schema are usable as documentation and prompt templates. The capability registry, composer, scoring engine, looper, and evaluation runner are design artifacts; their described behavior has not been implemented or validated as an executable system in this repository. Treat `evaluations/runner.md` command examples as proposed interfaces. Prompt text does not grant tool permissions or enforce runtime policy; execution controls belong to the host or separate tools.

## Repository guide

- [`framework.md`](framework.md) — the seven layers and their purpose.
- [`examples.md`](examples.md), [`templates.md`](templates.md) — examples and a copyable template.
- [`schemas/prompt.schema.yaml`](schemas/prompt.schema.yaml), [`schemas/prompt.sample.yaml`](schemas/prompt.sample.yaml) — illustrative YAML structures; no automated schema validator is shipped.
- [`docs/evaluation-layer.md`](docs/evaluation-layer.md) — manual review rubric.
- [`docs/architecture/capability-mesh-plan.md`](docs/architecture/capability-mesh-plan.md), [`registry/capabilities.yaml`](registry/capabilities.yaml), [`workflows/test-workflows.yaml`](workflows/test-workflows.yaml) — proposed capability model and sample workflows.
- [`evaluations/`](evaluations/) — proposed runner interface and sample fixtures.
- [`LICENSE`](LICENSE) — MIT reuse terms.

**Portfolio evidence:** [Systems & proof](https://drew-burt-portfolio.daxxer-os.chatgpt.site/systems)
