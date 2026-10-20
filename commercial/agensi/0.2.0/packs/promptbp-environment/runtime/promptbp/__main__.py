"""Offline PromptBP validation, governed compilation, and reported receipts."""

import argparse
import copy
import json
from pathlib import Path

import yaml

from .validation import validate_document, validate_file
from .spine import compile_intent, record_outcome


def _read_json(path):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("non-finite JSON value")

    with path.open("rb") as stream:
        data = stream.read(1_048_577)
    if len(data) > 1_048_576:
        raise ValueError("JSON input exceeds one MiB")
    return json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique_keys,
                      parse_constant=invalid_constant)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="check a prompt YAML document")
    validate.add_argument("path", type=Path)
    sub.add_parser("demo", help="check a valid sample and an invalid control offline")
    compile_command = sub.add_parser("compile", help="compile intent and separate operator context to JSON")
    compile_command.add_argument("path", type=Path)
    compile_command.add_argument("--context", type=Path, required=True)
    receipt_command = sub.add_parser("receipt", help="bind an executor-reported outcome; return a ledger entry")
    receipt_command.add_argument("compilation", type=Path)
    receipt_command.add_argument("observation", type=Path)
    args = parser.parse_args(argv)

    if args.command in ("compile", "receipt"):
        try:
            if args.command == "compile":
                result = compile_intent(_read_json(args.path), _read_json(args.context))
                code = {"ALLOW": 0, "REVIEW": 2, "HALT": 3}[result["gate"]["status"]]
            else:
                result = record_outcome(_read_json(args.compilation), _read_json(args.observation))
                code = 0
        except (OSError, UnicodeError, ValueError, TypeError, RecursionError):
            # Do not echo source content or parse exceptions that may contain private data.
            result = {"gate": {"status": "REVIEW", "reasons": ["input unreadable, invalid, or receipt binding failed"]},
                      "receipt": {"compiled": False, "execution_status": "not_started"}}
            code = 2
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return code

    if args.command == "validate":
        errors = validate_file(args.path)
        if errors:
            print("INVALID: " + "; ".join(errors))
            return 1
        print(f"VALID: {args.path} (structure only)")
        return 0

    sample = Path(__file__).resolve().parent.parent / "schemas" / "prompt.sample.yaml"
    document = yaml.safe_load(sample.read_text(encoding="utf-8"))
    valid = validate_document(document)
    bad = copy.deepcopy(document)
    bad["prompt"].pop("objective", None)
    invalid = validate_document(bad)
    print(f"Sample: {'VALID' if not valid else 'INVALID'} (structure only)")
    print(f"Missing objective: {'INVALID' if invalid else 'VALID'}")
    if invalid:
        print("Reason: " + "; ".join(invalid))
    print("No model call or tool execution occurred.")
    return 0 if not valid and any("prompt.objective" in error for error in invalid) else 1


if __name__ == "__main__":
    raise SystemExit(main())
