# Agensi skill packs — 0.2.0 release candidates

Two complete upload ZIP candidates and their unpacked source are included. Source: PromptBP commit 95f212b37b005db8b23bc0cf9109b27481565736. Runtime source files are unchanged.

| Candidate | Proposed price | Purpose |
| --- | --- | --- |
| PromptBP Repository Review Pack | $15 one-time | Bounded Codex review, evidence packet and reported receipt |
| PromptBP Task Environment Compiler | Free | Task directive, declared capabilities and approval gate |

Pricing is a proposal, not an approved listing or evidence of willingness to pay. Start with the review pack because it gives a buyer one concrete deliverable. The free compiler is the companion, not a claim of independent demand.

## Included
- archives/: two upload candidates, each with one top-level skill folder and SKILL.md.
- packs/: the exact unpacked archive contents, including runtime, upstream tests, buyer setup and templates.
- listings/: exact draft field text, permissions, FAQ and explicit incomplete-demo status.
- QA.json: performed package checks and checks not run.

## What changed from instruction-only packaging
Required compiler modules, schemas, sibling workflow and review helper now travel with each pack. No separate PromptBP checkout is needed. Python 3.10+ and PyYAML 6.x remain external dependencies. Neither pack claims universal native installation or runtime enforcement.

## Release gate
Current gate: REVIEW. Do not submit a candidate until the following evidence exists:
1. In each extracted pack's runtime directory, use an isolated Python environment with PyYAML and run:
```text
python -B -m unittest discover -s tests -v
python -B -m promptbp demo
python -B -m promptbp validate schemas/prompt.sample.yaml
```
2. Load the outer skill in the actual host, follow buyer setup, and perform a complete authorized task.
3. Capture the actual full user request and agent output for Agensi. Listing demo.result is intentionally null until that session exists.
4. Verify the Agensi upload/security result, review exact listing and price, obtain owner submission approval.

## Verification already performed
Required dependency file closure, exact runtime source-text equality, frontmatter required-field format, safe archive paths, and ZIP data/CRC/size roundtrip passed. Python and behavioral tests were not executed because no usable local execution environment was available. Historical upstream tests are included, not represented as newly passed.

## License and claims
MIT notices preserved. Source is also publicly available; paid value is packaging and workflow convenience. No exclusive IP license, support SLA, certification, guaranteed accuracy, legal compliance, autonomous operation or revenue guarantee is offered.

Agensi form requirements were read on 2026-10-20 at https://www.agensi.io/dashboard/submit: ZIP containing SKILL.md, under 50MB; name under 60 characters; listing, full real-session demo, compatibility, pricing and declared permissions. Its preview template was not treated as evidence of a passed security scan.

No marketplace upload, listing submission, publication, spending or customer outreach occurred.

## Follow-up execution test — 2026-10-20

Review Pack extraction, manual file-path loading, 54 bundled tests, offline demo, sample validation and starter compilation passed in Python 3.12.14 / PyYAML 6.0.3. All 22 runtime file hashes stayed unchanged. Native CLI installation remains untested.

The real repository-review attempt stopped correctly at REVIEW because this host does not expose its exact selected model/thinking settings. No model registry value was invented. A bound receipt records reported_blocked. The [actual full result](evidence/2026-10-20-review-pack/REAL_DEMO.md), [evaluation](evidence/2026-10-20-review-pack/EVALUATION.md), and raw logs are saved alongside this record. This is safety-path proof; it does not complete the successful live-review demo gate. These checks apply to the Review Pack archive, not an independent test of the Environment Pack.

Archive bytes remain unchanged so the tested artifact remains identifiable. Its original embedded provenance accurately describes the earlier packaging session; this dated external evidence supersedes its not-run status for the checks executed here. Publication remains unapproved.
