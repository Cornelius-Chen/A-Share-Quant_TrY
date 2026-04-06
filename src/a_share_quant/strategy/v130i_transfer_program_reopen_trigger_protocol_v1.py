from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130ITransferProgramReopenTriggerProtocolReport:
    summary: dict[str, Any]
    trigger_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "trigger_rows": self.trigger_rows,
            "interpretation": self.interpretation,
        }


class V130ITransferProgramReopenTriggerProtocolAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.freeze_path = repo_root / "reports" / "analysis" / "v130g_transfer_program_same_plane_support_freeze_v1.json"
        self.output_csv_path = repo_root / "data" / "training" / "transfer_program_reopen_watchlist_v1.csv"

    def analyze(self) -> V130ITransferProgramReopenTriggerProtocolReport:
        freeze = json.loads(self.freeze_path.read_text(encoding="utf-8"))

        trigger_rows = []
        for row in freeze["candidate_rows"]:
            same_plane_symbol_trigger_met = row["v6_symbol_count"] >= 2
            non_bridge_trigger_met = row["bridge_only"] is False and row["v6_symbol_count"] >= 2
            board_composite_trigger_met = (
                row["v6_board_composite"] is not None and row["v6_board_composite"] >= 0.45
            )
            reopen_ready = (
                same_plane_symbol_trigger_met
                and non_bridge_trigger_met
                and board_composite_trigger_met
            )
            trigger_rows.append(
                {
                    "sector_id": row["sector_id"],
                    "sector_name": row["sector_name"],
                    "current_v6_symbol_count": row["v6_symbol_count"],
                    "current_v5_symbol_count": row["v5_symbol_count"],
                    "current_v6_board_composite": row["v6_board_composite"],
                    "same_plane_symbol_trigger_threshold": 2,
                    "same_plane_symbol_trigger_met": same_plane_symbol_trigger_met,
                    "non_bridge_trigger_required": True,
                    "non_bridge_trigger_met": non_bridge_trigger_met,
                    "board_composite_trigger_threshold": 0.45,
                    "board_composite_trigger_met": board_composite_trigger_met,
                    "reopen_ready": reopen_ready,
                    "current_status": "blocked_waiting_for_richer_same_plane_support",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v130i_transfer_program_reopen_trigger_protocol_v1",
            "candidate_board_count": len(trigger_rows),
            "reopen_ready_count": sum(row["reopen_ready"] for row in trigger_rows),
            "authoritative_status": "transfer_program_frozen_with_explicit_reopen_triggers",
            "authoritative_rule": "a_new_board_worker_may_reopen_only_when_the_destination_board_has_multi_symbol_same_plane_support_non_bridge_semantics_and_acceptable_board_strength",
            "recommended_next_posture": "monitor_watchlist_and_reopen_only_when_any_candidate_hits_all_triggers",
        }
        interpretation = [
            "V1.30I converts the transfer-program freeze into an explicit reopen protocol.",
            "This keeps the methodology paused without losing operational readiness: the next board worker opens only when a candidate clears the same-plane, non-bridge, and strength triggers together.",
        ]
        return V130ITransferProgramReopenTriggerProtocolReport(
            summary=summary,
            trigger_rows=trigger_rows,
            interpretation=interpretation,
        )

    def write_watchlist_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(*, reports_dir: Path, report_name: str, result: V130ITransferProgramReopenTriggerProtocolReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V130ITransferProgramReopenTriggerProtocolAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130i_transfer_program_reopen_trigger_protocol_v1",
        result=result,
    )
    analyzer.write_watchlist_csv(result.trigger_rows)


if __name__ == "__main__":
    main()
