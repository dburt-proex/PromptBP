# Task Environment Pack — release candidate 0.2.0

## What you get
A workflow and offline compiler for translating a task and separate operator context into a directive, gate and optional capability manifest.
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

Ask: "Use this pack's SKILL.md to compile a task environment for my stated objective. Collect actual operator context separately, use only verified host capabilities, and return the manifest, directive, gate and compilation receipt."

Run from runtime with actual user inputs:
```text
python -B -m promptbp compile /ABSOLUTE/PATH/intent.json --context /ABSOLUTE/PATH/operator-context.json
```
Include a supported task_class in intent to request the environment layer. Missing required capability roles return REVIEW. See the bundled environment workflow for task classes and real inventory requirements.

## Limits and troubleshooting
- Exit 0 means compilation ALLOW, not execution completed. Exit 2 means REVIEW; exit 3 means HALT.
- A receipt command may exit 0 for a reported blocked outcome. Read execution_status.
- ModuleNotFoundError: confirm runtime is the working directory and the intended virtual environment is active.
- Missing PyYAML: complete setup separately; a read-only review does not authorize dependency installation.
- Missing inventory or unknown model settings: keep REVIEW; do not fabricate registry entries.
- No legal compliance, output accuracy, security enforcement, universal host compatibility or revenue guarantee is included.
- This distribution contains MIT-licensed source also available publicly. Payment, if approved, is for packaging and workflow convenience; no exclusive source-code rights or support SLA are implied.
