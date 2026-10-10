# PromptBP Compliance Readiness Baseline

Status: REVIEW  
Assessment date: 2026-08-16  
Canonical control registry: `dburt-proex/casa/governance/CONTROL-REGISTRY.yaml` v0.1

## Claim boundary

PromptBP may describe bounded capability contracts, prompt/version controls, evaluations, safety hooks, telemetry specifications and rollout/rollback controls where supported. It must not claim ISO/IEC certification, SOC 2 attestation or full compliance without independent assurance.

## Scope

PromptBP is assessed as the instruction/capability control layer: schemas, capability registry, block-boundary execution, evaluations, safety hooks, telemetry requirements, provider operating rules, staged rollout and rollback.

## Evidence-backed strengths

- Explicit capability contracts and bounded execution model.
- Prompt/capability schemas and registry.
- Evaluation fixtures and regression mechanisms.
- Input/output PII and injection safety hooks in the operating specification.
- Version-aware telemetry, staged rollout and rollback triggers.

## Gap register

| Priority | Control | Gap | Closure evidence |
|---|---|---|---|
| P0 | RSK-001 | Failure policies are not formal organizational risk treatment | risk register + treatment + residual-risk acceptance |
| P0 | LOG-001 | Logging is specified but canonical durable decision ledger is external | retained ledger/evidence receipt + integrity check |
| P0 | EVD-001 | Evaluation artifacts lack canonical provenance/retention binding | CASA evidence receipts + hashes + retention record |
| P0 | INC-001 | Rollback/investigation is not a complete incident lifecycle | IR SOP + tabletop + RCA + corrective-action/retest records |
| P0 | DAT-001 | PII/cache rules do not equal full data governance | data inventory/classification/retention/deletion/exception policy |
| P0 | SUP-001 | Provider limits are not supplier risk management | provider inventory + risk assessment + approved-use review |
| P0 | BCM-001 | Retry/circuit breaker/rollback is not tested recovery | backup/recovery policy + restore test + RTO/RPO evidence |
| P1 | IAM-001 | Capability contracts are not identity/access governance | identity/privilege matrix + periodic access review |
| P1 | CHG-001 | Change/evaluation evidence not canonically bound | PR/CI/evaluation receipt + commit binding |
| P1 | SEC-001 | Formal threat model/independent review absent | threat model + negative-path tests + security assessment |
| P1 | REV-001 | Regression review is not recurring internal audit/management review | audit report + management review + CAPA status |

## Validation workflow

1. Resolve all `COMPLIANCE.yaml` evidence paths against the assessed commit.
2. Execute available evaluation/regression and DiffWall workflows in an authorized environment.
3. Validate schema/registry consistency and capture the prompt/capability version under test.
4. Emit canonical CASA evidence receipts for each successful or failed control test.
5. Close or formally accept P0 risks.
6. Conduct internal readiness review before external assurance.

## Phase 10 entry criteria

External assurance remains blocked until P0 findings are closed or formally risk-treated, exact applicable framework requirements are mapped, evidence retention is established and management/operator review is recorded.
