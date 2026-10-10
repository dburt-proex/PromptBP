"""Prepare a read-only Codex review packet; no inventory discovery or dispatch."""
import argparse
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from promptbp.__main__ import _read_json
from promptbp.spine import compile_intent


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--source", choices=("github", "workspace"), required=True)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model")
    parser.add_argument("--thinking")
    args = parser.parse_args(argv)
    try:
        output = args.output.resolve()
        if output.is_relative_to(REPO) or output.exists():
            raise ValueError("output must be new and outside the compiler checkout")
        if args.source == "workspace":
            target = Path(args.target)
            if not target.is_absolute() or not target.is_dir() or output.is_relative_to(target.resolve()):
                raise ValueError("workspace target must exist; output must stay outside it")
        context = _read_json(args.context)
        if not isinstance(context, dict) or context.get("authority") != "read_only":
            raise ValueError("entry skill requires an explicit read_only operator context")
        request = {
            "intent": "Review repository state, recent meaningful activity and evidence-backed blockers.",
            "action": "inspect", "source": args.source, "target": args.target,
            "surface": "codex", "task_class": "repository_review",
            "constraints": ["Read only. Keep repository files and external accounts unchanged.",
                            "Do not expand authority, enable tools or change host settings."],
            "evidence_required": ["timestamped repository state", "recent activity evidence",
                                  "blocker evidence or explicitly labeled uncertainty", "before/after source state"],
            "acceptance_criteria": ["target verified", "repository state captured", "recent activity captured",
                                    "facts and uncertainties separated", "repository source preserved"],
        }
        if args.model is not None:
            request["model"] = args.model
        if args.thinking is not None:
            request["thinking"] = args.thinking
        compiled = compile_intent(request, context)
        if "context" not in compiled:
            print(json.dumps({"gate": "REVIEW", "packet": None, "reasons": compiled["gate"]["reasons"]}))
            return 2
        output.mkdir(parents=True, exist_ok=False)
        for name, value in (("intent.json", request), ("operator-context.json", context), ("compiled.json", compiled)):
            (output / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        status = compiled["gate"]["status"]
        print(json.dumps({"gate": status, "packet": str(output), "reasons": compiled["gate"]["reasons"],
                          "dispatch": "manual_handoff_only", "execution_status": "not_started"}))
        return {"ALLOW": 0, "REVIEW": 2, "HALT": 3}[status]
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError):
        # Never echo raw operator input, private parse details, or input values.
        print(json.dumps({"gate": "REVIEW", "packet": None,
                          "reasons": ["review packet preparation failed; verify read-only context and a new output directory outside repositories"]}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
