"""Individual assertion functions used by the runner.

Each returns a :class:`CheckResult` so the reporter can render a uniform
pass/fail table regardless of the check type.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
from jsonpath_ng import parse as parse_jsonpath


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


def check_status(expected: int, actual: int) -> CheckResult:
    passed = expected == actual
    detail = f"expected {expected}, got {actual}"
    return CheckResult("status", passed, detail)


def check_response_time(max_ms: int, elapsed_ms: float) -> CheckResult:
    passed = elapsed_ms <= max_ms
    detail = f"{elapsed_ms:.0f} ms (limit {max_ms} ms)"
    return CheckResult("response_time", passed, detail)


def validate_schema(schema_path: str | Path, body: Any) -> CheckResult:
    try:
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    except OSError as exc:
        return CheckResult("schema", False, f"cannot read schema: {exc}")
    try:
        jsonschema.validate(body, schema)
    except jsonschema.ValidationError as exc:
        location = "/".join(str(p) for p in exc.absolute_path) or "<root>"
        return CheckResult("schema", False, f"{location}: {exc.message}")
    return CheckResult("schema", True, f"matches {Path(schema_path).name}")


def extract_jsonpath(expr: str, data: Any) -> Any:
    """Return the first match for ``expr`` in ``data`` (or None)."""
    matches = parse_jsonpath(expr).find(data)
    return matches[0].value if matches else None


def check_jsonpath(expr: str, expected: Any, data: Any) -> CheckResult:
    actual = extract_jsonpath(expr, data)
    passed = actual == expected
    detail = f"{expr} -> {actual!r} (expected {expected!r})"
    return CheckResult(f"jsonpath {expr}", passed, detail)
