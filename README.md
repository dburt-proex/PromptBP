# PromptBP

PromptBP is a seven-layer prompt structure for making tasks, inputs, output shape, and review criteria explicit. This repository includes templates, a runnable structural YAML validator, illustrative fixtures, and a proposed capability architecture. It does not ship a model execution engine or an output-scoring harness.

## Install and verify

Requires Python 3.10+.

```bash
git clone https://github.com/dburt-proex/PromptBP.git
cd PromptBP
python -m pip install -e .
python -m promptbp validate schemas/prompt.sample.yaml
python -m promptbp demo
```

The commands report `VALID` for the included sample and `INVALID` when the demo removes its required objective. Validation checks document structure and nonempty fields; it does not score an LLM answer, enforce tool permissions, or establish output quality. The demo runs offline.

The validator package is version `0.1.0`. The `1.0.0` label in the sample YAML versions that sample prompt; it does not indicate a shipped execution runtime.

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

The seven layers and sample schema are usable as documentation and prompt templates. The validator checks the documented YAML structure. The capability registry, composer, scoring engine, looper, and output evaluation runner are design artifacts; their described behavior has not been implemented or validated as an executable system in this repository. Treat `evaluations/runner.md` command examples as proposed interfaces. Prompt text does not grant tool permissions or enforce runtime policy; execution controls belong to the host or separate tools.

## Repository guide

- [`framework.md`](framework.md) — the seven layers and their purpose.
- [`examples.md`](examples.md), [`templates.md`](templates.md) — examples and a copyable template.
- [`schemas/prompt.schema.yaml`](schemas/prompt.schema.yaml), [`schemas/prompt.sample.yaml`](schemas/prompt.sample.yaml) — documented YAML structure and sample; `python -m promptbp validate` checks the seven required layers.
- [`docs/evaluation-layer.md`](docs/evaluation-layer.md) — manual review rubric.
- [`docs/architecture/capability-mesh-plan.md`](docs/architecture/capability-mesh-plan.md), [`registry/capabilities.yaml`](registry/capabilities.yaml), [`workflows/test-workflows.yaml`](workflows/test-workflows.yaml) — proposed capability model and sample workflows.
- [`evaluations/`](evaluations/) — proposed runner interface and sample fixtures.
- [`LICENSE`](LICENSE) — MIT reuse terms.

**Portfolio evidence:** [Systems & proof](https://drew-burt-portfolio.daxxer-os.chatgpt.site/systems)
