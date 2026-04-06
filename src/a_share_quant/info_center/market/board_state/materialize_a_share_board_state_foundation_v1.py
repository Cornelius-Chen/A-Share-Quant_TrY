from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _parse_trade_date(value: str) -> datetime:
    if "-" in value:
        return datetime.strptime(value, "%Y-%m-%d")
    return datetime.strptime(value, "%Y%m%d")


def _format_trade_date(value: datetime) -> str:
    return value.strftime("%Y-%m-%d")


def _primary_state(states: list[str]) -> str:
    priority = {
        "lockout_worthy": 0,
        "unlock_worthy": 1,
        "false_bounce_only": 2,
    }
    return sorted(states, key=lambda item: priority.get(item, 99))[0]


@dataclass(slots=True)
class MaterializedAShareBoardStateFoundationV1:
    summary: dict[str, Any]
    board_rows: list[dict[str, Any]]
    interval_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareBoardStateFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.expectancy_path = (
            repo_root / "data" / "training" / "commercial_aerospace_board_expectancy_supervision_audit_v1.csv"
        )
        self.unlock_path = (
            repo_root / "data" / "training" / "commercial_aerospace_board_revival_unlock_audit_v1.csv"
        )
        self.lockout_path = (
            repo_root / "data" / "training" / "commercial_aerospace_board_cooling_lockout_audit_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "board_state_registry"
        self.surface_path = self.output_dir / "a_share_board_state_surface_v1.csv"
        self.interval_path = self.output_dir / "a_share_board_state_interval_registry_v1.csv"
        self.residual_path = self.output_dir / "a_share_board_state_residual_backlog_v1.csv"
        self.manifest_path = self.output_dir / "a_share_board_state_foundation_manifest_v1.json"

    def materialize(self) -> MaterializedAShareBoardStateFoundationV1:
        expectancy_rows = _read_csv(self.expectancy_path)
        unlock_rows = _read_csv(self.unlock_path)
        lockout_rows = _read_csv(self.lockout_path)

        lockout = lockout_rows[0]
        lockout_start = _parse_trade_date(lockout["lockout_start_trade_date"])
        lockout_end = _parse_trade_date(lockout["lockout_end_trade_date"])

        by_trade_date: dict[str, list[dict[str, str]]] = {}
        for row in expectancy_rows:
            by_trade_date.setdefault(row["trade_date"], []).append(row)

        unlock_seed_dates = {row["trade_date"] for row in unlock_rows if row["seed_role"] == "positive_revival_unlock_seed"}

        board_rows: list[dict[str, Any]] = []
        for trade_date in sorted(by_trade_date):
            rows = by_trade_date[trade_date]
            states = [row["expectancy_state"] for row in rows]
            primary_state = _primary_state(states)
            breadth_state = rows[0]["breadth_state"]
            support_evidence = "|".join(sorted({row["supporting_evidence"] for row in rows if row["supporting_evidence"]}))
            dt = _parse_trade_date(trade_date)
            lockout_active = lockout_start <= dt <= lockout_end
            board_rows.append(
                {
                    "board_id": "commercial_aerospace",
                    "board_name": "Commercial Aerospace",
                    "trade_date": _format_trade_date(dt),
                    "state_source": "expectancy_supervision",
                    "primary_board_state": primary_state,
                    "observed_state_set": "|".join(sorted(set(states))),
                    "breadth_state": breadth_state,
                    "unlock_seed_active": trade_date in unlock_seed_dates,
                    "lockout_active": lockout_active,
                    "board_drawdown": rows[0]["board_drawdown"],
                    "forward_board_return_20d": rows[0]["forward_board_return_20d"],
                    "reward_risk_ratio_20d": rows[0]["reward_risk_ratio_20d"],
                    "supporting_evidence": support_evidence,
                }
            )

        interval_rows = [
            {
                "board_id": "commercial_aerospace",
                "interval_type": "lockout_window",
                "start_trade_date": _format_trade_date(lockout_start),
                "end_trade_date": _format_trade_date(lockout_end),
                "interval_label": lockout["lockout_label"],
                "cooldown_guidance": lockout["cooldown_guidance"],
            }
        ]

        residual_rows = [
            {
                "residual_class": "multi_board_coverage_gap",
                "residual_reason": "board_state surface currently materialized only for commercial_aerospace bootstrap board",
            },
            {
                "residual_class": "post_lockout_extension_gap",
                "residual_reason": "commercial_aerospace board state remains bounded by the current lockout-aligned derivation boundary",
            },
            {
                "residual_class": "full_daily_board_surface_gap",
                "residual_reason": "surface is event-seed driven and not yet a full daily board-state timeline for all boards",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.surface_path, board_rows)
        _write(self.interval_path, interval_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "board_state_row_count": len(board_rows),
            "unlock_worthy_count": sum(row["primary_board_state"] == "unlock_worthy" for row in board_rows),
            "lockout_worthy_count": sum(row["primary_board_state"] == "lockout_worthy" for row in board_rows),
            "false_bounce_count": sum(row["primary_board_state"] == "false_bounce_only" for row in board_rows),
            "lockout_interval_count": len(interval_rows),
            "residual_count": len(residual_rows),
            "surface_path": str(self.surface_path.relative_to(self.repo_root)),
            "interval_path": str(self.interval_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareBoardStateFoundationV1(
            summary=summary, board_rows=board_rows, interval_rows=interval_rows, residual_rows=residual_rows
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareBoardStateFoundationV1(repo_root).materialize()
    print(result.summary["surface_path"])


if __name__ == "__main__":
    main()
