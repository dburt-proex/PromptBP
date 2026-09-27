# Seven-layer prompt template

Copy this into a model conversation and replace each bracketed field. The model host's instruction hierarchy and tool permissions still apply.

```text
ROLE: [Function and domain.]
OBJECTIVE: [One concrete, checkable result.]
INPUTS: [Source facts, required context, and known constraints.]
OUTPUT FORMAT: [Exact fields or sections and length.]
PERFORMANCE RULES: [Grounding and quality requirements; prohibited assumptions.]
STYLE: [Tone and density appropriate to the reader.]
RECURSIVE CHECK: [Specific checks to perform before answering.]
```

See [`examples.md`](examples.md) for filled examples and [`docs/evaluation-layer.md`](docs/evaluation-layer.md) for a manual rubric.
