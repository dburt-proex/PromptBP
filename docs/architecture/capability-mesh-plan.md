# PromptBP Capability Mesh Plan

Status: planning phase started 2026-06-26.

## Decision
PromptBP should evolve from a prompt template into a capability based execution system. The system should be built around reusable capabilities, not agent personalities.

## Goal
Create an auditable execution mesh that can classify intent, build state, compose workflows, execute capabilities, score outputs, loop failed sections back through the correct capability, and store lessons for reuse.

## Core flow

User intent -> Intent router -> State object builder -> Workflow composer -> Capability registry -> Capability mesh -> Scoring engine -> Looper -> Evaluation store -> Final output.

## Main components

1. State Object: one source of truth for objective, context, constraints, assumptions, decisions, evidence, artifacts, risks, validation, scores, and next actions.
2. Capability Contract: common interface for each capability, including name, purpose, input schema, output schema, required context, dependencies, cost class, latency class, reliability score, failure modes, confidence, risks, assumptions, and handoff.
3. Capability Registry: catalog used by the workflow composer to choose the right capability by fitness.
4. Workflow Composer: builds the execution chain from the registry based on intent, complexity, risk, and required output.
5. Scoring Engine: scores correctness, completeness, utility, risk, token efficiency, and confidence.
6. Looper: bounded improvement controller. It reruns only failed sections and stops when thresholds pass, improvement flattens, retry budget is exhausted, or human approval is required.
7. Evaluation Store: records workflow used, capabilities used, scores, failure modes, corrections, and reusable lessons.

## Immediate bottlenecks to prevent

- Mega orchestrator bottleneck: split routing, planning, and coordination.
- Context bloat: use a context broker and avoid sending full memory to every capability.
- Validation explosion: use one validation engine with pluggable checks.
- Retry storms: enforce max cycles and stop conditions.
- Prompt drift: use inheritance from kernel to capability rules to task context.
- Agent sprawl: build reusable capability primitives before specialized agents.

## MVP build order

1. Define State Object schema.
2. Define Capability Contract schema.
3. Create initial Capability Registry.
4. Implement Workflow Composer rules.
5. Add Scoring Engine.
6. Add Looper policy.
7. Add Evaluation Store.
8. Create PromptBP OS instruction blocks.
9. Add test workflows for audit, build, research, code review, and strategy.
10. Document failure policies and usage patterns.

## Initial capability set

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

## Acceptance criteria

- User intent converts into a structured State Object.
- Workflows compose from registry capabilities.
- Capabilities execute against a consistent contract.
- Output is scored across correctness, completeness, utility, risk, token efficiency, and confidence.
- Failed sections loop back only to the relevant capability.
- Final output records assumptions, risks, decisions, validation results, and next actions.
- Architecture avoids unnecessary multi-agent chatter.

## First implementation targets

- schemas/state-object.schema.json
- schemas/capability-contract.schema.json
- registry/capabilities.yaml
- docs/architecture/workflow-composer.md
- docs/architecture/looper-policy.md

## Conclusion
PromptBP becomes more valuable when it becomes an auditable, scored, reusable execution mesh. The Looper is the control circuit that turns one-pass generation into bounded recursive optimization.
