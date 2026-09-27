"""Small offline CLI for PromptBP prompt structure checks."""

import argparse
import copy
from pathlib import Path

import yaml

from .validation import validate_document, validate_file


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="check a prompt YAML document")
    validate.add_argument("path", type=Path)
    sub.add_parser("demo", help="check a valid sample and an invalid control offline")
    args = parser.parse_args(argv)

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
