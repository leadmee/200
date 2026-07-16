"""Load YAML collections / environments and interpolate ``{{variables}}``."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from apitester.models import Collection

_VAR = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")


def load_yaml(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_collection(path: str | Path) -> Collection:
    data = load_yaml(path)
    return Collection.model_validate(data)


def load_environment(env_file: str | Path, env_name: str) -> dict[str, Any]:
    """Return the variable map for ``env_name`` from an environments file."""
    data = load_yaml(env_file) or {}
    environments = data.get("environments", data)
    if env_name not in environments:
        available = ", ".join(environments) or "<none>"
        raise KeyError(f"Environment '{env_name}' not found in {env_file}. Available: {available}")
    return dict(environments[env_name])


def interpolate(value: Any, variables: dict[str, Any]) -> Any:
    """Recursively replace ``{{name}}`` placeholders using ``variables``.

    Non-string leaves (ints, bools, None) are returned unchanged. Unknown
    placeholders are left intact so failures are visible in the report.
    """
    if isinstance(value, str):
        def _repl(match: re.Match[str]) -> str:
            key = match.group(1)
            return str(variables[key]) if key in variables else match.group(0)

        return _VAR.sub(_repl, value)
    if isinstance(value, dict):
        return {k: interpolate(v, variables) for k, v in value.items()}
    if isinstance(value, list):
        return [interpolate(item, variables) for item in value]
    return value
