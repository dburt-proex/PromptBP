# PromptBP Review Pack — actual execution attempt

Date: October 20, 2026. Package: 0.2.0 release candidate.
Archive SHA-256: ed3a1cb1b4f6ad0c16f581b574c4cdc1430094cb3b7803716b6311c26e2583bc.
Source archive: PromptBP commit 39ad7a6b08cbeb99d5c0c57dfb0f9f837bcc0876, commercial/agensi/0.2.0/archives/promptbp-review-0.2.0-rc.zip.

## Actual owner request

> test the Review Pack end to end and capture its real demo—the remaining proof needed before your launch approval.

## Test scope selected for this request

Load the extracted outer SKILL.md and linked workflows by file path. Use the already available Python environment to verify the distribution. Attempt a read-only review of dburt-proex/PromptBP using actual owner authority and observed tools. Keep evidence outside the extracted pack. Stop at REVIEW or HALT; do not invent capabilities or switch models to force ALLOW.

## Complete deliverable from the actual attempt

**Result: REVIEW. The live repository review did not start.**

The downloaded archive passed Python zipfile CRC validation and contained 27 files. It was extracted and its outer entry, setup instructions, review workflow and environment workflow were loaded manually. Python 3.12.14 and PyYAML 6.0.3 were already installed; no dependency installation or host configuration change was made.

| Check | Observed result |
| --- | --- |
| Bundled unittest suite | 54 tests passed; exit 0 |
| Offline structural demo | Valid sample accepted; missing objective rejected; exit 0 |
| Sample schema validation | VALID; exit 0 |
| Illustrative starter compilation | ALLOW, execution not_started; exit 0 |
| Runtime source preservation | All 22 runtime files matched their before-run SHA-256 hashes |
| Live review packet preparation | REVIEW; exit 2 |
| Receipt generation | reported_blocked; exit 0 |
| Real repository findings and completed review | Not produced; substantive reads stopped at the gate |

The actual preparation command, run from the extracted runtime directory, was:

```text
python -B skills/promptbp-review/scripts/prepare_review.py --target dburt-proex/PromptBP --source github --context ACTUAL_OPERATOR_CONTEXT --output NEW_EXTERNAL_EVIDENCE_DIRECTORY
```

The exact gate reason was:

```text
requested model/thinking is unavailable; no substitute or model switch
```

The owner request supplies authority for this bounded test. Successful GitHub reads establish connector availability. The manually loaded workflow supplies the review skill role. The host does not expose its exact selected model ID or thinking level through the available session/configuration metadata. Therefore the operator registry intentionally contains no guessed model entry. The compiler preserved applied: false and returned REVIEW. It did not run the repository review, configure a model, expand permissions or claim completion.

The unchanged compiled packet was then bound to a real blocked observation through the receipt command. The command exited 0, but its receipt explicitly says reported_blocked. A zero receipt exit code is not a completed task.

**Next action:** obtain host-verified or owner-confirmed exact selected model and supported thinking level, without changing settings to bypass the gate. Recompile in a new evidence directory, complete the authorized review only after ALLOW, and capture its full findings and completed receipt. This blocked attempt is a real safety-path demonstration; it is not the completed buyer-result demo required for launch.

## Evidence

- validation.json and check-1 through check-4 logs: actual command results.
- runtime-hashes-before.json and runtime-hashes-after.json: preservation evidence.
- live-preparation.stdout.txt: actual gate response.
- actual-operator-context.json: actual declared authority and observed capability inventory.
- live-review-packet/compiled.json, observation.json, host-state.json and receipt.json: bound blocked run.

## Compatibility and release limits

This proves manual file-path loading and actual Python execution in this ChatGPT Work/Codex session. It does not prove native Codex CLI installation, independent cross-agent evaluation, Claude/Cursor/other host support, a completed live review, or an Agensi security scan. No marketplace fields were changed and no listing was submitted or published.
