# Looper Policy

## Purpose

The Looper is the control circuit that turns single-pass generation into bounded recursive optimization. It reruns only failed capabilities, respects budgets, and stops when improvement flattens.

## Core Rule

The Looper never reruns the entire workflow. It identifies the weakest scored section, routes it back to the specific capability responsible, and validates the improvement.

## Trigger Conditions

The Looper activates when any of the following are true:

```yaml
triggers:
  - score_below_threshold:
      any_dimension_below: 70
      aggregate_below: 75
  - validator_rejects:
      any_check_failed: true
  - risk_above_limit:
      risk_score_above: 80
  - ambiguity_unresolved:
      confidence_below: 60
  - output_too_verbose:
      token_efficiency_below: 50
```

## Stop Conditions

The Looper terminates when any of the following are true:

```yaml
stop_conditions:
  - all_required_scores_pass:
      min_correctness: 70
      min_completeness: 70
      min_utility: 70
      min_confidence: 60
      max_risk: 80
      min_token_efficiency: 50
  - improvement_delta_below_threshold:
      delta_percent: 5
      measured_over: "last_cycle"
  - retry_budget_exhausted:
      max_cycles: 3
  - human_approval_needed:
      risk_level: "critical"
      unresolved_ambiguity: true
  - capability_at_max_retries:
      per_capability_max: 2
```

## Execution Flow

```
1. Scoring Engine produces scores
2. IF all scores pass → proceed to delivery
3. IF any trigger fires:
   a. Identify failing dimensions
   b. Map failing dimensions to responsible capability
   c. Check: has this capability been rerun < max_retries?
   d. IF yes → rerun that capability with:
      - Original state object
      - Previous output (for reference)
      - Failure reason
      - Specific improvement instruction
   e. IF no → mark as "improvement exhausted" and proceed
4. After rerun, re-score
5. Evaluate stop conditions
6. IF stop condition met → exit loop
7. IF not → return to step 3 (up to max_cycles)
```

## Dimension-to-Capability Mapping

When a score fails, the Looper must know which capability to rerun:

| Failing Dimension | Primary Capability | Secondary Capability |
|-------------------|--------------------|---------------------|
| correctness | reasoning_engine | builder_generator |
| completeness | research_retrieval | reasoning_engine |
| utility | builder_generator | delivery_formatter |
| risk (too high) | risk_scanner | simulation_layer |
| token_efficiency | compression_engine | builder_generator |
| confidence | research_retrieval | reasoning_engine |

## Rerun Context

When the Looper reruns a capability, it provides:

```yaml
rerun_context:
  reason: ""              # why this rerun was triggered
  failing_scores:         # which dimensions failed
    - dimension: ""
      current_score: 0
      required_score: 0
  previous_output: ""     # what was produced last time
  specific_instruction: "" # what to fix
  attempt_number: 0       # which retry this is
  budget_remaining:
    cycles_left: 0
    tokens_left: 0
```

## Loop History

Every loop iteration is recorded in the state object:

```yaml
loop_history_entry:
  cycle: 1
  trigger: "score_below_threshold"
  failing_dimension: "completeness"
  capability_rerun: "research_retrieval"
  score_before: 62
  score_after: 78
  tokens_used: 340
  improvement_delta: 16
  outcome: "improved"  # improved | no_change | degraded
```

## Safety Rails

### 1. No Infinite Loops
- Hard cap: `max_cycles: 3` (configurable, never above 5)
- Per-capability cap: `max_retries: 2`

### 2. No Score Gaming
- If a rerun improves one dimension but degrades another by >10 points, flag as "trade-off loop" and stop

### 3. No Token Waste
- Track cumulative token cost of loops
- If loop tokens exceed 50% of original generation tokens, stop and flag

### 4. Degradation Detection
- If a rerun produces a lower score than the previous attempt, immediately stop looping that capability
- Record as "capability ceiling reached"

### 5. Human Escalation
- If after max_cycles, required scores still fail:
  - Mark state as `needs_review`
  - Include loop history in handoff
  - Present best attempt with explicit gap analysis

## Configuration

Default looper configuration:

```yaml
looper_config:
  enabled: true
  max_cycles: 3
  per_capability_max_retries: 2
  min_improvement_delta_percent: 5
  max_loop_token_ratio: 0.5
  score_thresholds:
    correctness: 70
    completeness: 70
    utility: 70
    risk: 80
    token_efficiency: 50
    confidence: 60
  escalation:
    on_budget_exhausted: "deliver_best_with_warnings"
    on_critical_failure: "halt_and_escalate"
    on_trade_off_loop: "deliver_with_trade_off_note"
```
