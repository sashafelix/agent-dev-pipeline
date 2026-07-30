#!/usr/bin/env python3
"""Small JSON Schema subset used by the local RGR contract validators.

Supported keywords: type, required, properties, additionalProperties, items,
enum, const, minItems, maxItems, uniqueItems, minLength, minimum, maximum,
and pattern. The subset is intentionally explicit and dependency-free.
"""
from __future__ import annotations

import json
import re
from typing import Any


def _matches_type(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, False)


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Return human-readable validation errors for one instance."""
    errors: list[str] = []

    expected = schema.get("type")
    if expected is not None:
        expected_types = [expected] if isinstance(expected, str) else expected
        if not isinstance(expected_types, list) or not all(isinstance(item, str) for item in expected_types):
            return [f"{path}: schema has invalid type declaration"]
        if not any(_matches_type(instance, item) for item in expected_types):
            return [f"{path}: expected type {expected_types}, got {type(instance).__name__}"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}, got {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}, got {instance!r}")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            errors.append(f"{path}: schema properties must be an object")
            properties = {}
        for key, child_schema in properties.items():
            if key in instance:
                errors.extend(validate_instance(instance[key], child_schema, f"{path}.{key}"))

        additional = schema.get("additionalProperties", True)
        if additional is False:
            unknown = sorted(set(instance) - set(properties))
            for key in unknown:
                errors.append(f"{path}: unexpected property {key!r}")
        elif isinstance(additional, dict):
            for key in sorted(set(instance) - set(properties)):
                errors.extend(validate_instance(instance[key], additional, f"{path}.{key}"))

    if isinstance(instance, list):
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        if isinstance(min_items, int) and len(instance) < min_items:
            errors.append(f"{path}: requires at least {min_items} item(s)")
        if isinstance(max_items, int) and len(instance) > max_items:
            errors.append(f"{path}: allows at most {max_items} item(s)")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in instance]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(validate_instance(item, item_schema, f"{path}[{index}]"))

    if isinstance(instance, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(instance) < min_length:
            errors.append(f"{path}: requires at least {min_length} character(s)")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, instance) is None:
            errors.append(f"{path}: does not match pattern {pattern!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and instance < minimum:
            errors.append(f"{path}: must be >= {minimum}")
        if isinstance(maximum, (int, float)) and instance > maximum:
            errors.append(f"{path}: must be <= {maximum}")

    return errors
