from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized_rows = rows or [{"row_state": "empty"}]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
        writer.writeheader()
        writer.writerows(materialized_rows)


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsRuntimeArtifactRetentionCapV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsRuntimeArtifactRetentionCapV1:
    HISTORY_MAX_ROWS = 1
    CLEANUP_LOG_MAX_ROWS = 1000

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.serving_registry_dir = (
            repo_root / "data" / "reference" / "info_center" / "serving_registry"
        )
        self.cleanup_log_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_retention_cleanup_log_v1.csv"
        )
        self.detail_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_runtime_artifact_retention_cap_detail_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_runtime_artifact_retention_cap_registry_v1.csv"
        )

    def _target_paths(self) -> list[tuple[Path, int, str]]:
        history_targets = sorted(self.serving_registry_dir.glob("*history_v1.csv"))
        targets = [(path, self.HISTORY_MAX_ROWS, "history_baseline_keep_latest") for path in history_targets]
        targets.append((self.cleanup_log_path, self.CLEANUP_LOG_MAX_ROWS, "cleanup_log_keep_recent_window"))
        return targets

    def materialize(self) -> MaterializedAShareInternalHotNewsRuntimeArtifactRetentionCapV1:
        detail_rows: list[dict[str, Any]] = []
        pruned_file_count = 0
        removed_row_count = 0

        for path, max_rows, cap_mode in self._target_paths():
            rows = _read_csv(path)
            before_count = len(rows)
            after_rows = rows
            removed_count = 0

            if before_count > max_rows:
                after_rows = rows[-max_rows:]
                removed_count = before_count - max_rows
                pruned_file_count += 1
                removed_row_count += removed_count
                _write_csv(path, after_rows)

            detail_rows.append(
                {
                    "artifact_path": str(path.relative_to(self.repo_root)),
                    "cap_mode": cap_mode,
                    "max_rows": str(max_rows),
                    "row_count_before": str(before_count),
                    "row_count_after": str(len(after_rows)),
                    "removed_row_count": str(removed_count),
                    "artifact_state": "pruned" if removed_count > 0 else "within_cap",
                }
            )

        summary_row = {
            "policy_id": "internal_hot_news_runtime_artifact_retention_cap",
            "scanned_file_count": str(len(detail_rows)),
            "pruned_file_count": str(pruned_file_count),
            "removed_row_count": str(removed_row_count),
            "history_max_rows": str(self.HISTORY_MAX_ROWS),
            "cleanup_log_max_rows": str(self.CLEANUP_LOG_MAX_ROWS),
            "policy_state": "bounded_runtime_artifacts_ready",
        }

        _write_csv(self.detail_path, detail_rows)
        _write_csv(self.registry_path, [summary_row])

        summary = {
            "scanned_file_count": len(detail_rows),
            "pruned_file_count": pruned_file_count,
            "removed_row_count": removed_row_count,
            "history_max_rows": self.HISTORY_MAX_ROWS,
            "cleanup_log_max_rows": self.CLEANUP_LOG_MAX_ROWS,
            "authoritative_output": "a_share_internal_hot_news_runtime_artifact_retention_cap_materialized",
        }
        return MaterializedAShareInternalHotNewsRuntimeArtifactRetentionCapV1(
            summary=summary,
            rows=detail_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsRuntimeArtifactRetentionCapV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
