from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@dataclass(slots=True)
class HotNewsRuntimeSwitchStateV1:
    enabled: bool
    row: dict[str, str]


class HotNewsRuntimeSwitchStoreV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_runtime_switch_v1.csv"
        )

    def read(self) -> HotNewsRuntimeSwitchStateV1:
        rows = _read_csv(self.path)
        if not rows:
            row = {
                "runtime_id": "internal_hot_news_runtime_scheduler",
                "runtime_enabled": "true",
                "updated_at_utc": "",
                "updated_by": "bootstrap_default",
                "notes": "default enabled until operator disables it",
            }
            _write_csv(self.path, [row])
            return HotNewsRuntimeSwitchStateV1(enabled=True, row=row)
        row = rows[0]
        return HotNewsRuntimeSwitchStateV1(
            enabled=row.get("runtime_enabled", "true").lower() == "true",
            row=row,
        )

    def write(self, *, enabled: bool, updated_by: str, notes: str) -> HotNewsRuntimeSwitchStateV1:
        row = {
            "runtime_id": "internal_hot_news_runtime_scheduler",
            "runtime_enabled": str(enabled).lower(),
            "updated_at_utc": datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_by": updated_by,
            "notes": notes,
        }
        _write_csv(self.path, [row])
        return HotNewsRuntimeSwitchStateV1(enabled=enabled, row=row)
