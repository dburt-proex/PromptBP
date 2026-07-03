# Usage Patterns and Failure Policies

## Usage Patterns

### Pattern 1: Simple Single-Pass

For low-complexity, low-risk tasks that need minimal orchestration.

```yaml
pattern: simple_single_pass
when:
  - complexity: low
  - risk: low
  - single clear objective
flow:
  intent_router → context_broker → builder_generator → scoring_engine → delivery_formatter
characteristics:
  - No looping expected
  - Minimal context assembly
  - Fast execution (< 30s total)
  - Token-efficient
```

### Pattern 2: Validated Build

For medium-complexity tasks where output correctness matters.

```yaml
pattern: validated_build
when:
  - complexity: medium
  - risk: medium
  - artifact must meet acceptance criteria
flow:
  intent_router → context_broker → constraint_resolver → builder_generator → validation_engine → scoring_engine → delivery_formatter
characteristics:
  - Validation gate before delivery
  - Loop possible on validation failure
  - Moderate token usage
  - 1-2 loop cycles typical
```

### Pattern 3: Deep Analysis

For high-complexity research or strategy tasks.

```yaml
pattern: deep_analysis
when:
  - complexity: high
  - requires evidence gathering
  - multiple perspectives needed
flow:
  intent_router → context_broker → research_retrieval → reasoning_engine → simulation_layer → risk_scanner → validation_engine → compression_engine → scoring_engine → delivery_formatter
characteristics:
  - Heavy research phase
  - Simulation for scenario comparison
  - Compression needed due to depth
  - Higher token budget required
  - 2-3 loop cycles common
```

### Pattern 4: Critical Decision

For critical-risk tasks requiring maximum governance.

```yaml
pattern: critical_decision
when:
  - risk: critical
  - irreversible consequences
  - multiple stakeholders
flow:
  intent_router → context_broker → constraint_resolver → research_retrieval → simulation_layer → reasoning_engine → risk_scanner → validation_engine → human_approval_gate → compression_engine → scoring_engine → delivery_formatter
characteristics:
  - Human gate required before delivery
  - Full risk assessment
  - Simulation of outcomes
  - Highest token budget
  - May require multiple human review cycles
```

### Pattern 5: Iterative Refinement

For tasks where the first output is expected to need improvement.

```yaml
pattern: iterative_refinement
when:
  - creative or subjective output
  - style calibration needed
  - user feedback loop expected
flow:
  intent_router → context_broker → builder_generator → scoring_engine → [looper] → delivery_formatter
characteristics:
  - Looper is primary mechanism
  - Multiple capability reruns expected
  - User feedback incorporated between loops
  - Budget managed carefully
```

---

## Failure Policies

### Policy 1: Capability Failure

When a single capability fails to produce valid output.

```yaml
policy: capability_failure
triggers:
  - capability returns error
  - capability output fails schema validation
  - capability exceeds timeout
actions:
  1. Log failure with full context
  2. Check: is there a fallback capability?
     - YES: route to fallback
     - NO: continue to step 3
  3. Check: is this capability required or optional?
     - REQUIRED: mark workflow as degraded, attempt retry (max 1)
     - OPTIONAL: skip and proceed with warning in state
  4. If retry also fails:
     - Record in state.validation.checks_failed
     - Proceed with partial output and explicit gap markers
     - Flag for human review if risk > medium
escalation:
  - After 2 failures of same capability in same workflow: halt
  - After 3 failures across different workflows in 1 hour: disable capability, alert
```

### Policy 2: Scoring Failure

When output scores below all thresholds after maximum loop cycles.

```yaml
policy: scoring_failure
triggers:
  - aggregate score < 50 after max_cycles
  - any critical dimension < 40 after max_cycles
actions:
  1. Mark state.handoff.status as "failed"
  2. Include in output:
     - Best attempt produced
     - Scores achieved vs required
     - Specific gaps identified
     - What the Looper tried and why it didn't work
  3. Recommend:
     - "Rerun with different constraints"
     - "Provide additional context for dimension X"
     - "Simplify objective"
  4. Store failure pattern in evaluation_store
escalation:
  - Notify prompt owner if same prompt fails > 3 times
  - Flag capability for review if it's the consistent failure point
```

### Policy 3: Context Starvation

When insufficient context is available for meaningful execution.

```yaml
policy: context_starvation
triggers:
  - context_broker flags missing critical context
  - capability confidence < 30 due to missing information
actions:
  1. Identify specific missing context items
  2. Check: can execution proceed with assumptions?
     - YES: state assumptions explicitly, reduce confidence score, proceed
     - NO: halt and request context
  3. If proceeding with assumptions:
     - Cap confidence at 50
     - Add warning to state.validation.warnings
     - Mark assumptions in state.assumptions
  4. Present user with:
     - "What I need to do better: [list]"
     - "What I assumed in the meantime: [list]"
     - "Confidence impact: reduced from X to Y"
```

### Policy 4: Token Budget Exceeded

When execution threatens to exceed allocated token budget.

```yaml
policy: token_budget_exceeded
triggers:
  - cumulative tokens > 80% of budget with capabilities remaining
  - single capability output > 50% of remaining budget
actions:
  1. At 80% budget used:
     - Enable compression_engine for all remaining outputs
     - Reduce remaining capabilities to essentials only
     - Skip optional validation checks
  2. At 95% budget used:
     - Deliver current best output immediately
     - Mark as "budget-constrained delivery"
     - Skip looper entirely
     - Include budget usage in trace
  3. Never exceed budget by > 10%
prevention:
  - Pre-estimate token usage per capability before execution
  - Alert at 60% threshold for adjustment
```

### Policy 5: Contradictory Constraints

When constraints cannot all be satisfied simultaneously.

```yaml
policy: contradictory_constraints
triggers:
  - constraint_resolver detects hard-hard conflict
  - constraint_resolver detects 3+ soft constraint conflicts
actions:
  1. Halt execution at constraint_resolver
  2. Present conflict clearly:
     - Constraint A: [description]
     - Constraint B: [description]
     - Why they conflict: [explanation]
  3. Offer resolution options:
     - "Prioritize A over B"
     - "Prioritize B over A"
     - "Relax A to soft constraint"
     - "Relax B to soft constraint"
     - "Provide additional context to resolve"
  4. Do not proceed until conflict is resolved
  5. Record resolution decision in state.decisions
```

### Policy 6: Looper Degradation

When the Looper makes things worse instead of better.

```yaml
policy: looper_degradation
triggers:
  - rerun score < previous score on target dimension
  - rerun improves target but degrades another by > 10 points
  - three consecutive loops with < 2 point improvement
actions:
  1. Immediately stop looping the affected capability
  2. Revert to best-scored version (not latest)
  3. Mark capability as "ceiling reached" for this execution
  4. If other dimensions still failing:
     - Try alternate capability mapping (secondary capability)
     - If secondary also degrades: accept and deliver with notes
  5. Record pattern in evaluation_store for future reference
```

### Policy 7: Human Escalation

When automated resolution is insufficient.

```yaml
policy: human_escalation
triggers:
  - risk_level: critical AND unresolved risks after scanning
  - confidence < 40 on any critical dimension after looping
  - contradictory constraints with no programmatic resolution
  - looper exhausted AND required scores not met
  - capability flagged requires_human_approval
actions:
  1. Compile escalation package:
     - Current state object (full)
     - Best output produced
     - Specific decision needed from human
     - Options with trade-offs
     - Time sensitivity (if any)
  2. Present in structured format:
     - "Decision required: [specific question]"
     - "Context: [minimal relevant context]"
     - "Options: [enumerated with pros/cons]"
     - "Recommendation: [if confidence > 50, provide one]"
     - "Risk of delay: [impact of not deciding]"
  3. Pause workflow until human responds
  4. On human response: integrate into state and resume
```

---

## Failure Mode Reference Table

| Failure Type | Severity | Auto-Recoverable | Max Retries | Escalation Trigger |
|---|---|---|---|---|
| Capability timeout | Medium | Yes | 2 | 3rd timeout |
| Schema validation fail | Low | Yes | 1 | 2nd fail |
| Score below threshold | Medium | Yes (via looper) | 3 cycles | Post-max cycles |
| Context starvation | High | Partial | 0 | Immediately |
| Constraint conflict | High | No | 0 | Immediately |
| Token budget exceeded | Medium | Yes (compression) | 0 | At 95% |
| Looper degradation | Medium | Yes (revert) | 1 | 2nd degradation |
| Critical risk unresolved | Critical | No | 0 | Immediately |
