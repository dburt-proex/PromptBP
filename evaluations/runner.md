# PromptBP Evaluation Runner

## Purpose

A lightweight harness that runs prompts against fixtures, scores them, and stores results alongside prompt versions to catch regressions.

## Usage

```bash
# Run all fixtures against a prompt
promptbp-eval run --prompt prompts/content-builder.yaml --fixtures evaluations/fixtures/

# Run a single fixture
promptbp-eval run --prompt prompts/content-builder.yaml --fixture evaluations/fixtures/content-builder-001.yaml

# Compare across versions
promptbp-eval diff --v1 1.0.0 --v2 1.1.0 --prompt prompts/content-builder.yaml
```

## Scoring Methods

### 1. Rule-Based Checks
- Schema conformance (output matches expected structure)
- Length compliance (within min/max bounds)
- Required field presence
- Forbidden pattern detection (e.g., filler phrases)

### 2. Regex / JSON Validation
- Output format validation (valid JSON, valid YAML, valid markdown structure)
- Pattern matching for required elements (headings, bullet counts, section markers)
- Negative pattern matching (banned words, generic phrases)

### 3. LLM-as-Judge (Optional)
- Prompt a secondary model to score the output on:
  - Correctness (0-5)
  - Completeness (0-5)
  - Style adherence (0-5)
  - Utility (0-5)
  - Specificity (0-5)
- Average scores across runs for statistical reliability

## Output Format

Results are stored as JSON:

```json
{
  "prompt": "content-builder",
  "version": "1.0.0",
  "fixture": "content-builder-001",
  "timestamp": "2026-07-01T12:00:00Z",
  "scores": {
    "schema_conformance": 5,
    "length_compliance": 4,
    "required_fields": 5,
    "forbidden_patterns": 5,
    "llm_correctness": 4,
    "llm_completeness": 4,
    "llm_style": 5,
    "llm_utility": 4,
    "llm_specificity": 4
  },
  "total": 40,
  "max_possible": 45,
  "pass": true,
  "notes": []
}
```

## Pass / Fail Thresholds

| Level | Score Range | Action |
|-------|-------------|--------|
| Pass | >= 80% | Deploy |
| Revise | 60-79% | Fix weakest layer |
| Reject | < 60% | Rebuild prompt |

## Regression Detection

When a new prompt version scores lower than the previous version on any fixture:
1. Flag the regression in output
2. Show score delta per dimension
3. Block deployment if delta exceeds 10% on any critical dimension (correctness, completeness)

## Fixture Structure

See `evaluations/fixtures/` for fixture format and examples.
