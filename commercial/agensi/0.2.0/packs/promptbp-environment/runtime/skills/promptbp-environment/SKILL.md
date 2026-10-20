---
name: promptbp-environment
description: Compile a bounded per-task execution environment for PromptBP directives from actual operator-declared capabilities, without enabling tools or expanding authority.
---

# PromptBP task environment compiler

Use after intent classification and before substantive work. Reuse the repository's
`python -m promptbp compile intent.json --context operator-context.json` command.
This is a repository skill asset, not an installed or activated plugin.

1. Establish the authoritative target and the owner's objective. Select a documented
   task class: `repository_review`, `software_change`, `buyer_research`, `resume`,
   `automation`, or `general`. Leave ambiguous classification at REVIEW.
2. Collect the separate operator context: authority reference, exact scope, available
   sources/surfaces, and a `capability_registry`. Inspect actual host availability;
   never treat legacy registry design entries or illustrative scores as proof.
3. Declare only supported model IDs/thinking levels and available tool, skill, and
   context references. Registry order is the owner's preference order. Do not infer
   capabilities, costs, success probabilities, or permissions from model names.
4. Compile. The manifest selects the minimum capability count within each kind,
   scoped to task class and surface. Buyer research and resumes must not inherit
   repository infrastructure merely because the owner has repositories.
5. If required roles, model/thinking, or references are missing, return REVIEW with
   the manifest issues. Preserve any HALT; never silently choose a fallback.
6. Return the manifest, directive, gate, and compilation receipt. Settings are
   proposed (`applied: false`). The host handles configuration and actual execution;
   approval is required before any authority expansion or external action.
7. After work, bind the executor observation to the unchanged compilation. Report
   missing/unrun checks. Return an evolution entry without changing canonical
   routing rules, authority, or skills. Training and autonomous rule updates are out
   of scope.

Acceptance: one bounded manifest with model/thinking, mode, selected skills/tools/
context references, authority, workspace, evidence, acceptance criteria, constraints,
stop conditions, and receipt requirements. Missing evidence never becomes ALLOW.

Intent routing remains in the existing compiler; this skill consumes its result.
Execution and enforcement remain with the host, CASA/Runwall or another authorized
executor. This skill does not integrate or replace those systems.
