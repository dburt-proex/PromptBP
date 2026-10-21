# Instruction-block state verification — October 21, 2026

Base: `95f212b37b005db8b23bc0cf9109b27481565736`.
Scope: state ownership and dependent-result invalidation in the instruction
blocks, plus an offline reference checker and regression evidence. Existing
compiler behavior and external execution permissions are unchanged.

## Changes

- One replacement output payload per capability, committed by the host to its
  own `state.results.<capability>.output` namespace. All twelve blocks declare
  exact fields and required dependency snapshots.
- Host-created revision/hash envelopes and retirement history. Every accepted
  replacement invalidates all transitive dependents. Obsolete in-flight results
  are rejected atomically; unaffected upstream results stay current.
- Separate Builder, Compression, and Formatter candidates. Risk scanning,
  validation, and scoring run after final formatting. Historical checks cannot
  satisfy readiness for a new candidate.
- Conflicting hard constraints are preserved and latch operator review. A later
  Resolver output cannot clear the latch. A host-recorded operator resolution
  invalidates affected work and sets the hard constraints the next result must
  retain.
- Readiness requires current results, every named host acceptance check passing,
  no context gaps or hard conflicts, passing numeric scores, and a current
  Looper proceed decision. It never authorizes external actions.

## Verification

Baseline: `python -m unittest discover -s tests -q` — 54 tests passed.
Before implementation, the initial ten new tests failed because the state
checker and ownership contract were absent. A follow-up conflict test also
demonstrated that clearing a conflict without operator resolution needed blocking.

Final commands:

```bash
python -m unittest discover -s tests -v
python -m promptbp demo
git diff --check
```

Results: **66 tests passed**, including **12 new state-contract tests**. The demo
accepted the valid structural sample, rejected a missing objective, and reported
no model call or tool execution. The whitespace check passed.

| Requested case | Observed offline result |
|---|---|
| Artifact changed after validation | Delivery readiness becomes false; dependent transforms, risk, validation, scoring, and Looper results are retired. Recomputing affected results restores readiness. Unaffected upstream analysis is retained. |
| Conflicting hard constraints | Both constraints remain in the Resolver report; downstream analysis is blocked. A replacement cannot silently clear review. Host-recorded resolution followed by recomputation restores readiness. |
| Malicious instructions in retrieved context | Attack text remains opaque source data. Attempts to add authority or another capability's validation fields to a Broker output are rejected without state mutation. Authority remains unchanged and delivery stays blocked. |

Additional coverage: stale in-flight validation, compression invalidation, failed
or unrun checks, high risk, unrelated/duplicate acceptance checks, snapshot/output
mutation isolation, unknown writers, wrong output types, missing fields, invalid
dependency graphs, and preserving operator-selected constraints.

## Evidence limits and next gate

These are deterministic offline tests with supplied capability output fixtures.
They establish state-control behavior, not whether generated content is true,
whether a model identifies contradictory prose, or whether a model resists prompt
injection. Conflict detection and check/score contents are caller reports. Hashes
and revision tokens are freshness aids, not authentication or tamper-proof proof.

The embedding host must authenticate writers and actual operator decisions,
isolate the checker from untrusted code, declare all upstream reads, and enforce
permissions before tools run. The checker implements the declared full build
reference path only. Existing composer workflows are not automatically migrated;
no autonomous loop, model adapter, delivery channel, or retry scheduler was added.

Next gate: review the code and contract, then integrate a host/model adapter and
repeat these cases against actual model outputs before making model-security or
end-to-end autonomous-execution claims. Merge and deployment remain owner decisions.
