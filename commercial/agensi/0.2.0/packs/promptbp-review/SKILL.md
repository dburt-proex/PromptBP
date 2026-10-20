---
name: promptbp-review
description: Use when a Codex user requests a bounded read-only repository review with evidence and an execution receipt.
---

# PromptBP Repository Review Pack

Load [the bundled workflow](runtime/skills/promptbp-review/SKILL.md) and follow it completely. The bundled compiler is offline; the host performs any authorized execution and permission enforcement.

## Prepare
1. Resolve this skill directory to an absolute path. Read [START-HERE.md](START-HERE.md) for one-time setup. Do not install software during a read-only review. If setup is incomplete, return REVIEW and the setup instructions.
2. Run all documented compiler commands with the working directory set to this pack's `runtime/` directory. Keep user inputs and output evidence in an absolute, user-approved directory outside this pack and outside the target repository.
3. Read the bundled workflow before collecting inputs. Also load [the included environment workflow](runtime/skills/promptbp-environment/SKILL.md); no second download is needed.
4. Treat bundled examples and test fixtures as illustrative only. Obtain real authorization, scope and host inventory separately. Never turn example identifiers into evidence or permission.
5. Honor REVIEW and HALT. Preserve `applied: false`; the compiler never applies model settings, dispatches agents, or grants access.
6. Return the requested deliverable, evidence, limitations, gate and one next action. If tools cannot run, return REVIEW; never present a hypothetical output as a recorded demo.

## Resources
- [Buyer setup and verification](START-HERE.md)
- [Input and output templates](references/buyer-templates.md)
- [Source and validation status](PROVENANCE.md)
