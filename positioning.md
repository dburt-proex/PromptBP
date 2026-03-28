# PromptBP Evaluation Layer

Use this layer to audit whether a PromptBP prompt is strong before deployment.

## Pass / Revise / Reject

### PASS
The prompt:
- has a clear role
- defines one concrete objective
- includes all necessary inputs
- forces a usable output format
- contains meaningful performance rules
- uses an intentional style
- includes a recursive review loop

### REVISE
The prompt works, but has weakness in one or more areas:
- role is generic
- objective is broad
- inputs are incomplete
- output format is too loose
- rules are soft or redundant
- style is vague
- recursive check is shallow

### REJECT
The prompt should be rebuilt if:
- objective is unclear
- output format is missing
- rules contradict each other
- inputs omit required context
- style does not match the use case
- the prompt relies on the model to guess too much

## Audit Questions

### Role
- Does the role materially improve execution?
- Is it specific enough to constrain behavior?

### Objective
- Can success be judged clearly?
- Is the task singular and unambiguous?

### Inputs
- Are all required facts, materials, and constraints present?
- Is missing context likely to cause failure?

### Output Format
- Would two strong outputs look structurally similar?
- Is the format directly usable?

### Performance Rules
- Are the rules enforceable?
- Do they eliminate known weak-output patterns?

### Style
- Is the tone intentionally selected?
- Does it match the audience and medium?

### Recursive Check
- Does it create a real quality loop?
- Does it force revision pressure before final output?

## Scoring Model

Optional 1-5 scoring:

- Role
- Objective
- Inputs
- Output Format
- Performance Rules
- Style
- Recursive Check

Total score:
- 30-35 = strong
- 24-29 = usable but needs refinement
- below 24 = weak prompt architecture
