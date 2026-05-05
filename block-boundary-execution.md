# Block Boundary Execution Layer

## Purpose

Block Boundary Execution is the PromptBP build protocol for repositories, sites, applications, integrations, and automation systems.

It replaces fragmented file-by-file prompting with controlled execution blocks that represent complete system slices.

## Core Rule

For build work, do not execute isolated files as separate tasks unless the file itself is the complete deliverable.

Execute by clean block boundaries.

A block must represent one of the following:
- feature
- route
- layer
- workflow
- integration
- migration
- validation pass
- deployable demo slice

## Mandatory Block Contract

Before execution, every block must define:

1. Block name
2. Objective
3. Scope included
4. Scope excluded
5. Files expected to change
6. Dependencies
7. Acceptance criteria
8. Risk notes
9. Rollback path
10. User acceptance gate

## Execution Rules

- One block must be coherent enough to review as a unit.
- One block must be small enough to validate without hidden scope creep.
- Prefer vertical slices when demo readiness or revenue validation matters.
- Prefer contract-first execution when APIs, schemas, integrations, or state changes are involved.
- Do not proceed to the next block until the current block is accepted.
- If a block touches production, credentials, payments, auth, security, data writes, deployment, or irreversible state, classify it as REVIEW or HALT until explicitly authorized.

## CASA-Gated Build Flow

User Request
→ PromptBP Block Contract
→ CASA Gate Classification
→ Execution
→ Validation
→ Change Summary
→ User Acceptance
→ Next Block

## Agent Swarm Compatibility

For supervised agent workflows, the block contract becomes the shared operating boundary.

Recommended agent roles:
- Supervisor: owns scope, sequencing, and final synthesis
- Builder: implements the block
- QA: validates behavior and acceptance criteria
- Governance: applies ALLOW / REVIEW / HALT classification
- Documentation: records changes, risks, and handoff notes

No agent may expand scope outside the active block without returning to the Supervisor and acceptance gate.

## Success Metrics

Track:
- first-pass acceptance rate
- number of rework loops per block
- defect rate after acceptance
- time from request to demoable artifact
- number of files changed per accepted block
- acceptance criteria pass/fail rate
- rollback clarity

## Failure Modes

Avoid:
- oversized blocks
- vague block contracts
- hidden dependencies
- non-demoable work
- premature infrastructure
- file-by-file fragmentation
- autonomous agent drift

## Default Block Size

A healthy block usually changes 2 to 6 files or one complete workflow surface.

Larger blocks are acceptable only when the integration boundary is cleaner than splitting the work.
