# PromptBP Capability Mesh Plan

Status: **implemented** — architecture defined and documented as of 2026-07-02.

## Executive Decision

PromptBP has evolved from a prompt framework into a capability-based execution architecture. It is built as a Capability Mesh with a Looper control circuit, scored state transitions, and reusable execution traces.

## Strategic Goal

PromptBP is now a governed execution operating system capable of routing intent, composing workflows, validating outputs, looping weak sections back through the correct capability, and storing reusable lessons.

## Core Architecture

```
User Intent
  ↓
Intent Router
  ↓
State Object Builder
  ↓
Workflow Composer
  ↓
Capability Registry
  ↓
Capability Mesh
  ├─ Context Broker
  ├─ Constraint Resolver
  ├─ Research / Retrieval
  ├─ Reasoning Engine
  ├─ Builder / Generator
  ├─ Simulation Layer
  ├─ Risk Scanner
  ├─ Validation Engine
  ├─ Compression Engine
  └─ Delivery Formatter
  ↓
Scoring Engine
  ↓
Looper
  ↓
Evaluation Store
  ↓
Reusable Memory
  ↓
Final Output
```

## Foundational Objects

### 1. State Object

Single source of truth for every workflow. Schema: `schemas/state-object.schema.yaml`

```yaml
state:
  objective:
  intent_type:
  complexity:
  risk_level:
  context:
  constraints:
  assumptions:
  decisions:
  evidence:
  artifacts:
  risks:
  validation:
  scores:
  next_actions:
```

### 2. Capability Contract

Every capability exposes the same execution interface. Schema: `schemas/capability-contract.schema.yaml`

```yaml
capability:
  name:
  purpose:
  input_schema:
  output_schema:
  required_context:
  dependencies:
  cost_class:
  latency_class:
  reliability_score:
  failure_modes:
  produces:
    confidence:
    risks:
    assumptions:
    handoff:
```

### 3. Capability Registry

The registry decides capability fitness before execution. See: `registry/capabilities.yaml`

### 4. Workflow Composer

Dynamically assembles workflows from capabilities. See: `docs/architecture/workflow-composer.md`

### 5. Scoring Engine

Every run receives objective scores. See: `docs/architecture/scoring-engine.md`

```yaml
scores:
  correctness: 0-100
  completeness: 0-100
  utility: 0-100
  risk: 0-100
  token_efficiency: 0-100
  confidence: 0-100
```

### 6. Looper

Controls recursive improvement. See: `docs/architecture/looper-policy.md`

```yaml
looper:
  trigger:
    - score_below_threshold
    - validator_rejects
    - risk_above_limit
    - ambiguity_unresolved
    - output_too_verbose
  max_cycles: 3
  stop_conditions:
    - all_required_scores_pass
    - improvement_delta_below_5_percent
    - retry_budget_exhausted
    - human_approval_needed
  rule:
    rerun_failed_capability_only: true
```

## Bottlenecks Prevented

| Bottleneck | Prevention |
|---|---|
| Mega orchestrator | Split routing, planning, and coordination |
| Context bloat | Context Broker with minimal-sufficient assembly |
| Validation explosion | One Validation Engine with plug-in checks |
| Retry storms | Looper with max cycles and stop conditions |
| Prompt drift | Inheritance: Kernel → Capability Rules → Task Context |
| Agent sprawl | Capabilities as primitives, not personalities |

## MVP Build Order (Completed)

- [x] Define State Object schema → `schemas/state-object.schema.yaml`
- [x] Define Capability Contract schema → `schemas/capability-contract.schema.yaml`
- [x] Create initial Capability Registry → `registry/capabilities.yaml`
- [x] Implement Workflow Composer logic → `docs/architecture/workflow-composer.md`
- [x] Add Scoring Engine → `docs/architecture/scoring-engine.md`
- [x] Add Looper control policy → `docs/architecture/looper-policy.md`
- [x] Add Evaluation Store → defined in registry and state schema
- [x] Create PromptBP OS instruction block templates → `templates/os-instruction-blocks.md`
- [x] Create test workflows → `workflows/test-workflows.yaml`
- [x] Document usage patterns and failure policies → `docs/architecture/usage-patterns-and-failure-policies.md`

## Capability Set

- intent_router
- context_broker
- constraint_resolver
- workflow_composer
- reasoning_engine
- builder_generator
- research_retrieval
- simulation_layer
- risk_scanner
- validation_engine
- compression_engine
- delivery_formatter
- scoring_engine
- looper
- evaluation_store

## Acceptance Criteria

- ✅ A user intent can be converted into a structured State Object
- ✅ A workflow can be composed from registry capabilities
- ✅ Capabilities execute against a consistent contract
- ✅ Output scored across correctness, completeness, utility, risk, token efficiency, and confidence
- ✅ Failed sections loop back only to the relevant capability
- ✅ Final output includes traceable assumptions, risks, decisions, and validation results
- ✅ Architecture remains token-efficient and avoids unnecessary multi-agent chatter

## Repository Structure

```
schemas/
  prompt.schema.yaml          # canonical prompt schema
  prompt.sample.yaml          # validated sample prompt
  state-object.schema.yaml    # state object definition
  capability-contract.schema.yaml  # capability interface contract

registry/
  capabilities.yaml           # full capability catalog

templates/
  os-instruction-blocks.md    # reusable instruction blocks for each capability

workflows/
  test-workflows.yaml         # reference test workflows (audit, build, research, review, strategy)

evaluations/
  runner.md                   # evaluation harness documentation
  fixtures/                   # test fixtures for prompt evaluation

docs/
  operations.md               # timeouts, caching, batching, telemetry, safety hooks
  style-vectors.md            # tone/voice calibration exemplars
  architecture/
    capability-mesh-plan.md   # this document
    workflow-composer.md       # workflow composition rules
    looper-policy.md          # looper control policy
    scoring-engine.md         # scoring dimensions and methods
    usage-patterns-and-failure-policies.md  # usage patterns and failure handling
```

## Conclusion

PromptBP is now an auditable, scored, reusable execution mesh. The Looper is the control circuit that turns one-pass generation into bounded recursive optimization. The architecture is capability-first, governance-aware, and designed for token efficiency.
