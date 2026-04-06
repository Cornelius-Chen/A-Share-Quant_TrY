from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class MaterializedAShareLiveLikeViewBootstrapV1:
    summary: dict[str, Any]
    event_state_rows: list[dict[str, Any]]
    gate_view_rows: list[dict[str, Any]]
    registry_rows: list[dict[str, Any]]


class MaterializeAShareLiveLikeViewBootstrapV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.shadow_path = (
            repo_root / "data" / "derived" / "info_center" / "replay" / "shadow" / "a_share_shadow_replay_surface_v1.csv"
        )
        self.review_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_review_activation_registry_v1.csv"
        )
        self.source_activation_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_activation_registry_v1.csv"
        )
        self.gate_path = (
            repo_root / "data" / "reference" / "info_center" / "governance_registry" / "a_share_promotion_gate_registry_v1.csv"
        )
        self.serving_dir = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.live_like_dir = repo_root / "data" / "derived" / "info_center" / "replay" / "live_like"
        self.event_state_path = self.live_like_dir / "a_share_live_like_event_state_surface_v1.csv"
        self.gate_view_path = self.serving_dir / "a_share_live_like_execution_gate_view_v1.csv"
        self.registry_path = self.serving_dir / "a_share_live_like_view_materialization_registry_v1.csv"
        self.manifest_path = self.serving_dir / "a_share_live_like_view_bootstrap_manifest_v1.json"

    def materialize(self) -> MaterializedAShareLiveLikeViewBootstrapV1:
        shadow_rows = _read_csv(self.shadow_path)
        review_rows = _read_csv(self.review_registry_path)
        source_rows = _read_csv(self.source_activation_path)
        gate_rows = _read_csv(self.gate_path)

        active_local_ingest_count = sum(row["activation_state"] == "active_local_ingest" for row in source_rows)
        active_review_queue_count = sum(row["queue_state"] == "active_bootstrap" for row in review_rows)
        closed_gates = [row["gate_id"] for row in gate_rows if row["gate_state"] == "closed"]

        event_state_rows: list[dict[str, Any]] = []
        for row in shadow_rows:
            if row["replay_status"] == "shadow_replay_context_ready":
                live_like_state = "candidate_context_ready_but_gate_closed"
            elif row["replay_status"] == "intraday_only_shadow_watch":
                live_like_state = "candidate_intraday_only_watch"
            elif row["replay_status"] == "daily_only_shadow_watch":
                live_like_state = "candidate_daily_only_watch"
            else:
                live_like_state = "candidate_context_blocked"
            event_state_rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_ts": row["decision_ts"],
                    "decision_trade_date": row["decision_trade_date"],
                    "shadow_replay_status": row["replay_status"],
                    "live_like_state": live_like_state,
                    "closed_gate_count": len(closed_gates),
                    "active_local_ingest_count": active_local_ingest_count,
                    "active_review_queue_count": active_review_queue_count,
                }
            )

        gate_view_rows = [
            {
                "gate_id": row["gate_id"],
                "gate_state": row["gate_state"],
                "gate_reason": row["gate_reason"],
                "live_like_impact": "blocking" if row["gate_state"] == "closed" else "non_blocking_bootstrap",
            }
            for row in gate_rows
        ]

        registry_rows = [
            {
                "view_id": "live_like_event_state_surface",
                "consumer_mode": "live_like",
                "artifact_path": str(self.event_state_path.relative_to(self.repo_root)),
                "view_state": "materialized_but_blocked",
            },
            {
                "view_id": "live_like_execution_gate_view",
                "consumer_mode": "live_like",
                "artifact_path": str(self.gate_view_path.relative_to(self.repo_root)),
                "view_state": "materialized_but_blocked",
            },
        ]

        for path in (self.serving_dir, self.live_like_dir):
            path.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.event_state_path, event_state_rows)
        _write(self.gate_view_path, gate_view_rows)
        _write(self.registry_path, registry_rows)

        summary = {
            "event_state_row_count": len(event_state_rows),
            "candidate_intraday_only_watch_count": sum(
                row["live_like_state"] == "candidate_intraday_only_watch" for row in event_state_rows
            ),
            "candidate_context_blocked_count": sum(
                row["live_like_state"] == "candidate_context_blocked" for row in event_state_rows
            ),
            "closed_gate_count": len(closed_gates),
            "registry_path": str(self.registry_path.relative_to(self.repo_root)),
            "event_state_path": str(self.event_state_path.relative_to(self.repo_root)),
            "gate_view_path": str(self.gate_view_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareLiveLikeViewBootstrapV1(
            summary=summary,
            event_state_rows=event_state_rows,
            gate_view_rows=gate_view_rows,
            registry_rows=registry_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareLiveLikeViewBootstrapV1(repo_root).materialize()
    print(result.summary["registry_path"])


if __name__ == "__main__":
    main()
