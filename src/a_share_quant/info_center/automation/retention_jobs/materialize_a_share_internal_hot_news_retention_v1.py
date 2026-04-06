from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
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
class MaterializedAShareInternalHotNewsRetentionV1:
    summary: dict[str, Any]
    policy_rows: list[dict[str, Any]]
    queue_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsRetentionV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.fastlane_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_fastlane_surface_v1.csv"
        )
        self.policy_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_retention_policy_v1.csv"
        )
        self.queue_path = (
            repo_root
            / "data"
            / "temp"
            / "info_center"
            / "retention_queue"
            / "a_share_internal_hot_news_retention_queue_v1.csv"
        )
        self.cleanup_log_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_retention_cleanup_log_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsRetentionV1:
        fastlane_rows = _read_csv(self.fastlane_path)
        existing_queue_rows = [
            row
            for row in _read_csv(self.queue_path)
            if row.get("telegraph_id")
        ]

        policy_rows = [
            {
                "retention_class": "hot_layer_ttl_5d",
                "ttl_days": "5",
                "retention_action": "delete_hot_copy_after_ttl",
            },
            {
                "retention_class": "promote_to_important_layer",
                "ttl_days": "5",
                "retention_action": "delete_hot_copy_after_ttl_keep_important_copy",
            },
        ]

        existing_queue_map = {row["telegraph_id"]: row for row in existing_queue_rows}
        active_queue_rows: list[dict[str, Any]] = []
        cleanup_rows: list[dict[str, Any]] = []
        now_utc = datetime.now(tz=UTC)
        for row in fastlane_rows:
            fetch_ts = datetime.strptime(row["fetch_ts_utc"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            expiry_ts = (fetch_ts + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
            active_queue_rows.append(
                {
                    "telegraph_id": row["telegraph_id"],
                    "title": row["title"],
                    "promotion_target": row["promotion_target"],
                    "hot_layer_expiry_ts_utc": expiry_ts,
                    "important_layer_retained": str(row["promotion_target"] == "promote_to_important_layer"),
                    "retention_queue_state": "awaiting_ttl_cleanup",
                }
            )

        active_ids = {row["telegraph_id"] for row in active_queue_rows}
        for row in existing_queue_rows:
            telegraph_id = row["telegraph_id"]
            if telegraph_id in active_ids:
                continue
            expiry_dt = datetime.strptime(row["hot_layer_expiry_ts_utc"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            if expiry_dt > now_utc:
                active_queue_rows.append(
                    {
                        **row,
                        "retention_queue_state": "awaiting_ttl_cleanup",
                    }
                )
            else:
                cleanup_rows.append(
                    {
                        "telegraph_id": telegraph_id,
                        "title": row.get("title", ""),
                        "promotion_target": row.get("promotion_target", ""),
                        "hot_layer_expiry_ts_utc": row.get("hot_layer_expiry_ts_utc", ""),
                        "important_layer_retained": row.get("important_layer_retained", "False"),
                        "cleanup_recorded_at_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S"),
                        "cleanup_state": (
                            "expired_hot_copy_deleted_keep_important"
                            if row.get("important_layer_retained", "False") == "True"
                            else "expired_hot_copy_deleted"
                        ),
                    }
                )

        active_queue_rows.sort(key=lambda row: (row["hot_layer_expiry_ts_utc"], row["telegraph_id"]))

        summary = {
            "policy_row_count": len(policy_rows),
            "retention_queue_count": len(active_queue_rows),
            "expired_cleanup_count": len(cleanup_rows),
            "important_retained_count": sum(
                row["important_layer_retained"] == "True" for row in active_queue_rows
            ),
            "policy_path": str(self.policy_path.relative_to(self.repo_root)),
            "queue_path": str(self.queue_path.relative_to(self.repo_root)),
            "cleanup_log_path": str(self.cleanup_log_path.relative_to(self.repo_root)),
        }

        _write_csv(self.policy_path, policy_rows)
        _write_csv(self.queue_path, active_queue_rows)
        _write_csv(self.cleanup_log_path, cleanup_rows)
        return MaterializedAShareInternalHotNewsRetentionV1(
            summary=summary,
            policy_rows=policy_rows,
            queue_rows=active_queue_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsRetentionV1(repo_root).materialize()
    print(result.summary["policy_path"])


if __name__ == "__main__":
    main()
