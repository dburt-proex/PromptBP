# Changelog

## 1.0.0 - 2026-07-02
- **MAJOR**: Evolved PromptBP from prompt framework to capability-based execution architecture
- Executed all upgrades from upgrades.md:
  - Added canonical prompt schema with versioning and provenance (schemas/prompt.schema.yaml)
  - Added validated sample prompt (schemas/prompt.sample.yaml)
  - Added evaluation harness with fixtures (evaluations/)
  - Added operations documentation: timeouts, caching, batching, telemetry, safety hooks (docs/operations.md)
  - Added style vectors with tone/voice exemplars (docs/style-vectors.md)
- Implemented Capability Mesh Architecture:
  - State Object schema (schemas/state-object.schema.yaml)
  - Capability Contract schema (schemas/capability-contract.schema.yaml)
  - Capability Registry with 15 capabilities (registry/capabilities.yaml)
  - Workflow Composer with composition rules (docs/architecture/workflow-composer.md)
  - Scoring Engine with 6 dimensions (docs/architecture/scoring-engine.md)
  - Looper control policy with bounded recursion (docs/architecture/looper-policy.md)
  - OS instruction block templates for all capabilities (templates/os-instruction-blocks.md)
  - Test workflows: audit, build, research, code review, strategy (workflows/test-workflows.yaml)
  - Usage patterns and failure policies (docs/architecture/usage-patterns-and-failure-policies.md)
- Updated capability-mesh-plan.md to reflect completed implementation
- Updated README with full repository guide

## 0.1.1 - 2026-03-31
- added upgrade recommendations for performance, effectiveness, and operational hardening
- refreshed README to surface key docs

## 0.1.0 - 2026-03-28
- initial repository scaffold
- added PromptBP framework documentation
- added evaluation layer
- added examples and reusable templates
- added positioning notes
