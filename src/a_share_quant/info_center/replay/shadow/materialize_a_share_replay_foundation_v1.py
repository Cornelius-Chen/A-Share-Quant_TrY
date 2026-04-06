from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MaterializedAShareReplayFoundationV1:
    summary: dict[str, Any]
    shadow_rows: list[dict[str, Any]]
    lane_rows: list[dict[str, Any]]
    backlog_rows: list[dict[str, Any]]


class MaterializeAShareReplayFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.time_slice_path = (
            repo_root / "data" / "derived" / "info_center" / "time_slices" / "a_share_time_slice_view_v1.csv"
        )
        self.transition_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "state_transition_journal"
            / "a_share_state_transition_journal_v1.csv"
        )
        self.daily_market_path = (
            repo_root / "data" / "reference" / "info_center" / "market_registry" / "a_share_daily_market_registry_v1.csv"
        )
        self.intraday_coverage_path = (
            repo_root / "data" / "reference" / "info_center" / "market_registry" / "a_share_intraday_coverage_registry_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "replay_registry"
        self.shadow_dir = repo_root / "data" / "derived" / "info_center" / "replay" / "shadow"
        self.shadow_surface_path = self.shadow_dir / "a_share_shadow_replay_surface_v1.csv"
        self.lane_registry_path = self.output_dir / "a_share_shadow_lane_registry_v1.csv"
        self.backlog_path = self.output_dir / "a_share_shadow_replay_backlog_v1.csv"
        self.manifest_path = self.output_dir / "a_share_replay_foundation_manifest_v1.json"

    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def materialize(self) -> MaterializedAShareReplayFoundationV1:
        time_slice_rows = self._read_csv(self.time_slice_path)
        transition_rows = self._read_csv(self.transition_path)
        daily_market_rows = self._read_csv(self.daily_market_path)
        intraday_rows = self._read_csv(self.intraday_coverage_path)

        daily_start = min(row["first_trade_date"] for row in daily_market_rows)
        daily_end = max(row["last_trade_date"] for row in daily_market_rows)
        intraday_dates = {row["trade_date"] for row in intraday_rows}

        shadow_rows: list[dict[str, Any]] = []
        for row in time_slice_rows:
            trade_date = row["decision_ts"][:10].replace("-", "")
            daily_trade_date = row["decision_ts"][:10]
            intraday_ready = trade_date in intraday_dates
            daily_ready = daily_start <= daily_trade_date <= daily_end
            if intraday_ready and daily_ready:
                replay_status = "shadow_replay_context_ready"
            elif intraday_ready and not daily_ready:
                replay_status = "intraday_only_shadow_watch"
            elif daily_ready and not intraday_ready:
                replay_status = "daily_only_shadow_watch"
            else:
                replay_status = "shadow_replay_blocked_missing_market_context"
            shadow_rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_ts": row["decision_ts"],
                    "decision_trade_date": daily_trade_date,
                    "visible_event_count": row["visible_event_count"],
                    "visible_high_conf_event_count": row["visible_high_conf_event_count"],
                    "intraday_zip_available": intraday_ready,
                    "daily_market_available": daily_ready,
                    "replay_status": replay_status,
                }
            )

        event_visibility_count = sum(row["transition_class"] == "event_visibility" for row in transition_rows)
        attention_transition_count = sum(row["transition_class"] == "attention_bootstrap" for row in transition_rows)
        lane_rows = [
            {
                "shadow_lane_id": "a_share_shadow_lane_v1",
                "lane_state": "read_only_bootstrap",
                "shadow_surface_row_count": len(shadow_rows),
                "event_visibility_transition_count": event_visibility_count,
                "attention_transition_count": attention_transition_count,
                "replay_promotive": False,
            }
        ]
        backlog_rows = [
            {
                "replay_component": "execution_binding",
                "backlog_reason": "shadow replay is read-only and not yet linked to lawful execution journals",
            },
            {
                "replay_component": "cost_model_binding",
                "backlog_reason": "cost model registry remains deferred until live_like serving is in place",
            },
            {
                "replay_component": "market_context_alignment",
                "backlog_reason": "daily bootstrap coverage is narrow and does not yet align with all shadow slices",
            },
        ]

        for path in (self.output_dir, self.shadow_dir):
            path.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.shadow_surface_path, shadow_rows)
        _write(self.lane_registry_path, lane_rows)
        _write(self.backlog_path, backlog_rows)

        summary = {
            "shadow_surface_row_count": len(shadow_rows),
            "shadow_context_ready_count": sum(row["replay_status"] == "shadow_replay_context_ready" for row in shadow_rows),
            "intraday_only_watch_count": sum(row["replay_status"] == "intraday_only_shadow_watch" for row in shadow_rows),
            "daily_only_watch_count": sum(row["replay_status"] == "daily_only_shadow_watch" for row in shadow_rows),
            "blocked_count": sum(
                row["replay_status"] == "shadow_replay_blocked_missing_market_context" for row in shadow_rows
            ),
            "lane_registry_path": str(self.lane_registry_path.relative_to(self.repo_root)),
            "shadow_surface_path": str(self.shadow_surface_path.relative_to(self.repo_root)),
            "backlog_path": str(self.backlog_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareReplayFoundationV1(
            summary=summary,
            shadow_rows=shadow_rows,
            lane_rows=lane_rows,
            backlog_rows=backlog_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareReplayFoundationV1(repo_root).materialize()
    print(result.summary["shadow_surface_path"])


if __name__ == "__main__":
    main()
