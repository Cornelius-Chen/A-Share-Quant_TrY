from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


def load_yaml_config(path: Path) -> dict[str, Any]:
    """Load a YAML config file into a dictionary."""
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Config at {path} must decode to a mapping.")
    return payload


def merge_config(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge a config override into a base config."""
    merged = deepcopy(base)
    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = merge_config(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged
