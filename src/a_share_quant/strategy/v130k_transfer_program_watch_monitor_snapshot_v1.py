from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130KTransferProgramWatchMonitorSnapshotReport:
    summary: dict[str, Any]
    monitor_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "monitor_rows": self.monitor_rows,
            "interpretation": self.interpretation,
        }


class V130KTransferProgramWatchMonitorSnapshotAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.trigger_path = repo_root / "reports" / "analysis" / "v130i_transfer_program_reopen_trigger_protocol_v1.json"
        self.output_csv_path = repo_root / "data" / "training" / "transfer_program_watch_monitor_snapshot_v1.csv"

    def analyze(self) -> V130KTransferProgramWatchMonitorSnapshotReport:
        trigger_report = json.loads(self.trigger_path.read_text(encoding="utf-8"))
        monitor_rows: list[dict[str, Any]] = []
        for row in trigger_report["trigger_rows"]:
            current_board_composite = row["current_v6_board_composite"]
            board_gap = None
            if current_board_composite is not None:
                board_gap = max(0.0, row["board_composite_trigger_threshold"] - current_board_composite)
            missing_trigger_count = sum(
                1
                for key in (
                    "same_plane_symbol_trigger_met",
                    "non_bridge_trigger_met",
                    "board_composite_trigger_met",
                )
                if row[key] is False
            )
            monitor_rows.append(
                {
                    "sector_id": row["sector_id"],
                    "sector_name": row["sector_name"],
                    "current_v6_symbol_count": row["current_v6_symbol_count"],
                    "current_v5_symbol_count": row["current_v5_symbol_count"],
                    "current_v6_board_composite": current_board_composite,
                    "missing_trigger_count": missing_trigger_count,
                    "same_plane_symbol_gap": max(
                        0,
                        row["same_plane_symbol_trigger_threshold"] - row["current_v6_symbol_count"],
                    ),
                    "board_composite_gap": board_gap,
                    "bridge_only_or_not_ready": not row["non_bridge_trigger_met"],
                    "reopen_ready": row["reopen_ready"],
                    "monitor_priority": self._priority_key(
                        missing_trigger_count=missing_trigger_count,
                        board_gap=board_gap,
                        current_board_composite=current_board_composite,
                    ),
                }
            )

        monitor_rows.sort(
            key=lambda item: (
                item["missing_trigger_count"],
                item["same_plane_symbol_gap"],
                item["board_composite_gap"] if item["board_composite_gap"] is not None else 999.0,
                -(item["current_v6_board_composite"] or 0.0),
                item["sector_id"],
            )
        )

        closest = monitor_rows[0] if monitor_rows else None
        summary = {
            "acceptance_posture": "freeze_v130k_transfer_program_watch_monitor_snapshot_v1",
            "candidate_board_count": len(monitor_rows),
            "reopen_ready_count": sum(row["reopen_ready"] for row in monitor_rows),
            "closest_candidate_sector_id": closest["sector_id"] if closest else None,
            "closest_candidate_sector_name": closest["sector_name"] if closest else None,
            "authoritative_status": "freeze_transfer_program_and_monitor_gap_closure",
            "authoritative_rule": "keep_the_transfer_program_frozen_until_any_watchlist_candidate_closes_the_same_plane_non_bridge_and_board_strength_gaps_together",
        }
        interpretation = [
            "V1.30K converts the reopen watchlist into a ranked monitor snapshot.",
            "The goal is not to reopen a worker early, but to make the gap-to-readiness explicit and comparable across boards.",
        ]
        return V130KTransferProgramWatchMonitorSnapshotReport(
            summary=summary,
            monitor_rows=monitor_rows,
            interpretation=interpretation,
        )

    @staticmethod
    def _priority_key(*, missing_trigger_count: int, board_gap: float | None, current_board_composite: float | None) -> str:
        board_gap_repr = "na" if board_gap is None else f"{board_gap:.6f}"
        composite_repr = "na" if current_board_composite is None else f"{current_board_composite:.6f}"
        return f"m{missing_trigger_count}_g{board_gap_repr}_c{composite_repr}"

    def write_snapshot_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(*, reports_dir: Path, report_name: str, result: V130KTransferProgramWatchMonitorSnapshotReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V130KTransferProgramWatchMonitorSnapshotAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130k_transfer_program_watch_monitor_snapshot_v1",
        result=result,
    )
    analyzer.write_snapshot_csv(result.monitor_rows)


if __name__ == "__main__":
    main()
