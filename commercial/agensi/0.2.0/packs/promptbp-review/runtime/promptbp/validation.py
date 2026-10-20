"""Validate the documented seven-layer YAML prompt structure.

This checks document shape and required content; it does not evaluate model output.
"""

from pathlib import Path

import yaml


def _text(value, path, errors):
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected nonempty text")


def _text_list(value, path, errors, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        errors.append(f"{path}: expected {'nonempty ' if nonempty else ''}list of text")
    elif any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(f"{path}: each item must be nonempty text")


def _mapping(value, path, errors):
    if not isinstance(value, dict):
        errors.append(f"{path}: expected mapping")
        return {}
    return value


def validate_document(document):
    """Return structural errors for a PromptBP document; empty means valid."""
    errors = []
    root = _mapping(document, "document", errors)
    prompt = _mapping(root.get("prompt"), "prompt", errors)
    metadata = _mapping(prompt.get("metadata"), "prompt.metadata", errors)
    for key in ("version", "owner", "last_review_date", "model_target", "status"):
        _text(metadata.get(key), f"prompt.metadata.{key}", errors)
    _text_list(metadata.get("tags"), "prompt.metadata.tags", errors)

    role = _mapping(prompt.get("role"), "prompt.role", errors)
    for key in ("description", "domain", "posture"):
        _text(role.get(key), f"prompt.role.{key}", errors)
    _text(prompt.get("objective"), "prompt.objective", errors)

    inputs = _mapping(prompt.get("inputs"), "prompt.inputs", errors)
    _text_list(inputs.get("required"), "prompt.inputs.required", errors, nonempty=True)
    _text_list(inputs.get("optional"), "prompt.inputs.optional", errors)
    _text(inputs.get("source_of_truth"), "prompt.inputs.source_of_truth", errors)
    _text_list(inputs.get("constraints"), "prompt.inputs.constraints", errors)

    output = _mapping(prompt.get("output_format"), "prompt.output_format", errors)
    _text_list(output.get("structure"), "prompt.output_format.structure", errors, nonempty=True)
    for key in ("format_type", "max_length"):
        _text(output.get(key), f"prompt.output_format.{key}", errors)
    _text_list(prompt.get("performance_rules"), "prompt.performance_rules", errors, nonempty=True)

    style = _mapping(prompt.get("style"), "prompt.style", errors)
    for key in ("tone", "density", "voice"):
        _text(style.get(key), f"prompt.style.{key}", errors)
    _text_list(prompt.get("recursive_check"), "prompt.recursive_check", errors, nonempty=True)

    if "grounding" in prompt:
        grounding = _mapping(prompt["grounding"], "prompt.grounding", errors)
        for key in ("citation_required", "hallucination_check"):
            if key in grounding and not isinstance(grounding[key], bool):
                errors.append(f"prompt.grounding.{key}: expected boolean")
        if "retrieval_sources" in grounding:
            _text_list(grounding["retrieval_sources"], "prompt.grounding.retrieval_sources", errors)
    return errors


def validate_file(path):
    """Read and validate a YAML file, returning error strings."""
    try:
        document = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return [f"{path}: {exc}"]
    return validate_document(document)
