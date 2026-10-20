# Repository Review Pack — release candidate 0.2.0

## What you get
A workflow for a bounded read-only repository review, an offline packet-preparation helper, and reported execution receipts.
The full required PromptBP runtime, schemas, sibling skills and upstream tests are included. Python 3.10+ and PyYAML 6.x remain external requirements.

## Set up once, before a review
Extract the ZIP. In a terminal open its `runtime` directory. Create a virtual environment outside the target repository:
```text
python -m venv /ABSOLUTE/PATH/promptbp-venv
```
Activate it using your operating system's normal activation command. Inspect the bundled code and dependency declaration, then install PyYAML from your trusted source:
```text
python -m pip install "PyYAML>=6,<7"
python -B -m unittest discover -s tests -v
python -B -m promptbp demo
python -B -m promptbp validate schemas/prompt.sample.yaml
```
Installing PyYAML may require network access. No OpenAI API key or model API billing is required by the compiler. Your agent host has its own access and billing requirements. Never put credentials in operator-context files.

## First offline smoke check
Run from `runtime`:
```text
python -B -m promptbp compile examples/vnext/intent.json --context examples/vnext/operator-context.json
```
The upstream-documented expected result is an ALLOW compilation with execution not_started. This is a synthetic starter, not a real review, verified authorization, or a task-environment manifest. It makes no model call and does not inspect the example repository.

## Use with your agent
Load the outer SKILL.md by absolute path using your host's skill loader or ask your agent to read that file and its linked workflow. Hosts that cannot read local files or execute Python cannot run the complete workflow. Native install paths vary by host and have not been tested for this release candidate.

Ask: "Use this pack's SKILL.md to review OWNER/REPOSITORY read-only. Use my current authorization and your actual available tools. Put the packet and evidence in an absolute directory outside this pack and the target. Stop at REVIEW or HALT."

The agent must build real operator context first. The original helper command, run from runtime, is:
```text
python -B skills/promptbp-review/scripts/prepare_review.py --target OWNER/REPOSITORY --source github --context /ABSOLUTE/PATH/operator-context.json --output /ABSOLUTE/PATH/new-review-packet
```
The output directory must not already exist. Use --source workspace and an absolute target directory for a local review. Preparation writes local evidence files; source repositories and external accounts stay unchanged.

## Limits and troubleshooting
- Exit 0 means compilation ALLOW, not execution completed. Exit 2 means REVIEW; exit 3 means HALT.
- A receipt command may exit 0 for a reported blocked outcome. Read execution_status.
- ModuleNotFoundError: confirm runtime is the working directory and the intended virtual environment is active.
- Missing PyYAML: complete setup separately; a read-only review does not authorize dependency installation.
- Missing inventory or unknown model settings: keep REVIEW; do not fabricate registry entries.
- No legal compliance, output accuracy, security enforcement, universal host compatibility or revenue guarantee is included.
- This distribution contains MIT-licensed source also available publicly. Payment, if approved, is for packaging and workflow convenience; no exclusive source-code rights or support SLA are implied.
