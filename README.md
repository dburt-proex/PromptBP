# PromptBP

**Portfolio evidence:** [Systems & proof](https://drew-burt-portfolio.daxxer-os.chatgpt.site/systems)

Constrained, systematic prompting framework evolved into a capability-based execution architecture that produces controlled, high-fidelity responses from language models.

## What is PromptBP?

PromptBP is a governed execution operating system that routes intent, composes workflows from reusable capabilities, validates outputs with objective scoring, and loops weak sections back through the correct capability for bounded recursive optimization.

## Contents

### Core Framework
- `examples.md` — Prompt examples using the 7-layer framework
- `templates.md` — Reusable prompt templates (legacy format)
- `operator-prompts.md` — Operator positioning and context
- `framework.md` — The PromptBP 7-layer framework definition
- `block-boundary-execution.md` — Block-based build execution protocol

### Capability Mesh Architecture
- `docs/architecture/capability-mesh-plan.md` — Full architecture plan and status
- `docs/architecture/workflow-composer.md` — How workflows are composed from capabilities
- `docs/architecture/scoring-engine.md` — Scoring dimensions and methods
- `docs/architecture/looper-policy.md` — Bounded recursive improvement controller
- `docs/architecture/usage-patterns-and-failure-policies.md` — Usage patterns and failure handling

### Schemas
- `schemas/prompt.schema.yaml` — Canonical prompt schema with versioning
- `schemas/prompt.sample.yaml` — Validated sample prompt
- `schemas/state-object.schema.yaml` — State object (single source of truth per workflow)
- `schemas/capability-contract.schema.yaml` — Capability execution interface contract

### Registry
- `registry/capabilities.yaml` — Full capability catalog with fitness criteria

### Templates
- `templates/os-instruction-blocks.md` — OS-level instruction blocks for each capability

### Workflows
- `workflows/test-workflows.yaml` — Reference test workflows (audit, build, research, review, strategy)

### Evaluation
- `evaluations/runner.md` — Evaluation harness documentation
- `evaluations/fixtures/` — Test fixtures for prompt regression testing

### Operations
- `docs/operations.md` — Timeouts, caching, batching, telemetry, safety hooks, rollout strategy
- `docs/style-vectors.md` — Tone/voice calibration exemplars

### Guidance
- `positioning.md` — PromptBP positioning and audience
- `upgrades.md` — Upgrade recommendations (executed)

## Quick Start

1. **Define intent** — What do you need? (audit, build, research, review, strategy)
2. **Check the workflow composer** — See `docs/architecture/workflow-composer.md` for how capabilities are assembled
3. **Use OS instruction blocks** — See `templates/os-instruction-blocks.md` for capability prompts
4. **Score your output** — Apply the scoring dimensions from `docs/architecture/scoring-engine.md`
5. **Loop if needed** — Let the Looper policy handle failed sections

## Architecture Overview

```
User Intent → Intent Router → State Object → Workflow Composer → Capability Mesh → Scoring Engine → Looper → Final Output
```

Key principles:
- **Capabilities over agents**: Reusable primitives, not personalities
- **Scored execution**: Every output is objectively measured
- **Bounded recursion**: The Looper improves weak sections without retry storms
- **Token efficiency**: Context Broker prevents bloat; Compression Engine optimizes delivery
- **Traceable**: Every assumption, decision, and risk is recorded in the state object
