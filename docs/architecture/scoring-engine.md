# Scoring Engine

## Purpose

The Scoring Engine provides objective, standardized scoring for every workflow execution. It enables the Looper to make informed decisions, tracks quality over time, and supports regression detection.

## Scoring Dimensions

Every execution output is scored across six dimensions:

| Dimension | Range | Measures | Lower Threshold |
|-----------|-------|----------|-----------------|
| Correctness | 0-100 | Factual accuracy, logical soundness, requirement adherence | 70 |
| Completeness | 0-100 | Coverage of all required elements, no gaps | 70 |
| Utility | 0-100 | Practical value, actionability, usability | 70 |
| Risk | 0-100 | Identified risks and their severity (lower is better) | 80 (max acceptable) |
| Token Efficiency | 0-100 | Information density, no waste | 50 |
| Confidence | 0-100 | Certainty of outputs, evidence backing | 60 |

## Scoring Methods

### Method 1: Rule-Based Scoring

Deterministic checks applied automatically:

```yaml
rule_checks:
  correctness:
    - schema_valid: "output matches expected structure"
    - no_contradictions: "no internal logical conflicts"
    - requirements_met: "all acceptance criteria addressed"
  completeness:
    - all_sections_present: "required output sections exist"
    - no_placeholders: "no TODO or TBD markers"
    - inputs_consumed: "all required inputs used"
  utility:
    - actionable: "contains concrete next steps"
    - specific: "no generic filler"
    - usable_format: "output is directly consumable"
  risk:
    - risks_identified: "known risks are surfaced"
    - mitigations_present: "each risk has a response"
    - no_critical_unaddressed: "no critical risks without mitigation"
  token_efficiency:
    - within_budget: "output tokens <= allocated budget"
    - no_repetition: "no redundant content"
    - information_density: "high signal-to-noise ratio"
  confidence:
    - evidence_cited: "claims have supporting evidence"
    - assumptions_explicit: "assumptions are stated"
    - uncertainty_flagged: "uncertain areas are marked"
```

### Method 2: LLM-as-Judge

For dimensions that require judgment, use a scoring prompt:

```yaml
judge_prompt:
  role: "Expert output quality assessor"
  objective: "Score the following output on {dimension}"
  inputs:
    - original_objective
    - output_to_score
    - scoring_criteria
  output_format: "Score (0-100) + one-line justification"
  performance_rules:
    - "Be calibrated: 50 means average, 70 means good, 90 means excellent"
    - "Never give 100 unless output is flawless"
    - "Justify with specific evidence from the output"
    - "Penalize generality and filler"
```

### Method 3: Comparative Scoring

When baseline exists, score relative to previous best:

```yaml
comparative:
  method: "delta from baseline"
  baseline_source: "evaluation_store"
  improvement_bonus: 5  # bonus points if better than baseline
  regression_penalty: 10  # penalty if worse than baseline
```

## Aggregate Score

```yaml
aggregate:
  method: "weighted_average"
  weights:
    correctness: 0.25
    completeness: 0.20
    utility: 0.20
    risk: 0.15
    token_efficiency: 0.10
    confidence: 0.10
  pass_threshold: 70
  fail_threshold: 50
```

## Score Interpretation

| Aggregate Score | Interpretation | Action |
|----------------|----------------|--------|
| 90-100 | Excellent | Deliver, store as exemplar |
| 75-89 | Good | Deliver, note improvement areas |
| 60-74 | Acceptable | Deliver with caveats, or loop |
| 40-59 | Weak | Loop required, flag for review |
| 0-39 | Failed | Halt, escalate, do not deliver |

## Scoring Triggers

The Scoring Engine runs:
1. After every capability produces output (inline scoring)
2. At the end of the composed workflow (final scoring)
3. After every Looper rerun (improvement scoring)
4. On demand for evaluation/regression testing

## Output Format

```yaml
scoring_result:
  timestamp: ""
  workflow_id: ""
  scores:
    correctness: 0
    completeness: 0
    utility: 0
    risk: 0
    token_efficiency: 0
    confidence: 0
  aggregate: 0
  pass: false
  failing_dimensions: []
  justifications:
    correctness: ""
    completeness: ""
    utility: ""
    risk: ""
    token_efficiency: ""
    confidence: ""
  recommendation: ""  # deliver | loop | escalate | halt
  loop_target: ""     # capability to rerun if recommendation is "loop"
```

## Calibration

### Score Consistency

To prevent score drift:
1. Use fixed scoring rubrics (not open-ended evaluation)
2. Calibrate against stored exemplars monthly
3. Track score distribution over time
4. Alert if mean scores shift >10 points over 30 days

### Anti-Gaming

Prevent capabilities from optimizing for scores at the expense of quality:
1. Rotate scoring rubrics periodically
2. Include "surprise" evaluation dimensions quarterly
3. Cross-validate with human spot-checks (5% of runs)
4. Penalize outputs that match scoring criteria literally but miss intent
