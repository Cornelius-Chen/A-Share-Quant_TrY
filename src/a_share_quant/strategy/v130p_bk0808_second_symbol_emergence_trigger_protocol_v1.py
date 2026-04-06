from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130PBK0808SecondSymbolEmergenceTriggerProtocolReport:
    summary: dict[str, Any]
    trigger_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "trigger_rows": self.trigger_rows,
            "interpretation": self.interpretation,
        }


class V130PBK0808SecondSymbolEmergenceTriggerProtocolAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.watch_path = repo_root / "reports" / "analysis" / "v130n_bk0808_military_civil_fusion_local_emergence_watch_audit_v1.json"
        self.reopen_path = repo_root / "reports" / "analysis" / "v130i_transfer_program_reopen_trigger_protocol_v1.json"
        self.output_csv_path = repo_root / "data" / "training" / "bk0808_second_symbol_emergence_trigger_v1.csv"

    def analyze(self) -> V130PBK0808SecondSymbolEmergenceTriggerProtocolReport:
        watch_report = json.loads(self.watch_path.read_text(encoding="utf-8"))
        reopen_report = json.loads(self.reopen_path.read_text(encoding="utf-8"))
        bk0808_row = next(row for row in reopen_report["trigger_rows"] if row["sector_id"] == "BK0808")

        trigger_rows = []
        for row in watch_report["candidate_rows"]:
            if row["recommended_watch_status"] != "nearest_same_plane_watch":
                continue
            emergence_would_close_same_plane_gap = row["v6_snapshot_days"] == 0 and bk0808_row["current_v6_symbol_count"] == 1
            board_strength_already_sufficient = bk0808_row["board_composite_trigger_met"] is True
            emergence_would_clear_bridge_only = emergence_would_close_same_plane_gap
            reopen_candidate_if_emerged = (
                emergence_would_close_same_plane_gap
                and board_strength_already_sufficient
                and emergence_would_clear_bridge_only
            )
            trigger_rows.append(
                {
                    "symbol": row["symbol"],
                    "watch_status": row["recommended_watch_status"],
                    "timeline_approval_days": row["timeline_approval_days"],
                    "timeline_leader_core_days": row["timeline_leader_core_days"],
                    "timeline_first_date": row["timeline_first_date"],
                    "timeline_last_date": row["timeline_last_date"],
                    "current_v6_snapshot_days": row["v6_snapshot_days"],
                    "current_board_composite": bk0808_row["current_v6_board_composite"],
                    "emergence_requirement": "gain_any_v6_same_plane_snapshot_support_inside_BK0808",
                    "emergence_would_close_same_plane_gap": emergence_would_close_same_plane_gap,
                    "emergence_would_clear_bridge_only": emergence_would_clear_bridge_only,
                    "board_strength_already_sufficient": board_strength_already_sufficient,
                    "reopen_candidate_if_emerged": reopen_candidate_if_emerged,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v130p_bk0808_second_symbol_emergence_trigger_protocol_v1",
            "nearest_second_symbol_count": len(trigger_rows),
            "single_symbol_emergence_sufficient_count": sum(row["reopen_candidate_if_emerged"] for row in trigger_rows),
            "authoritative_status": "bk0808_can_only_move_from_frozen_to_reopen_candidate_if_600118_or_an_equivalent_watch_name_appears_in_v6_same_plane_support",
            "authoritative_rule": "do_not_reopen_the_worker_on_timeline_support_alone; require_actual_v6_same_plane_emergence",
        }
        interpretation = [
            "V1.30P converts the BK0808 watchlist into an explicit symbol-emergence trigger.",
            "The important point is that 600118 is not merely interesting; if it gains real v6 same-plane support while board strength holds, BK0808 would become a reopen candidate without any additional narrative stretch.",
        ]
        return V130PBK0808SecondSymbolEmergenceTriggerProtocolReport(
            summary=summary,
            trigger_rows=trigger_rows,
            interpretation=interpretation,
        )

    def write_trigger_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(*, reports_dir: Path, report_name: str, result: V130PBK0808SecondSymbolEmergenceTriggerProtocolReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V130PBK0808SecondSymbolEmergenceTriggerProtocolAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130p_bk0808_second_symbol_emergence_trigger_protocol_v1",
        result=result,
    )
    analyzer.write_trigger_csv(result.trigger_rows)


if __name__ == "__main__":
    main()
