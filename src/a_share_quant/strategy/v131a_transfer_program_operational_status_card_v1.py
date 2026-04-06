from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131ATransferProgramOperationalStatusCardReport:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V131ATransferProgramOperationalStatusCardAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.bundle_path = repo_root / "reports" / "analysis" / "v130v_transfer_program_governance_bundle_v1.json"
        self.readiness_path = repo_root / "reports" / "analysis" / "v130z_transfer_program_reopen_readiness_status_v1.json"
        self.output_csv_path = repo_root / "data" / "training" / "transfer_program_operational_status_card_v1.csv"

    def analyze(self) -> V131ATransferProgramOperationalStatusCardReport:
        bundle = json.loads(self.bundle_path.read_text(encoding="utf-8"))
        readiness = json.loads(self.readiness_path.read_text(encoding="utf-8"))

        bk0808 = next(row for row in bundle["bundle_rows"] if row["sector_id"] == "BK0808")
        status_rows = [
            {"status_key": "program_status", "status_value": "frozen"},
            {"status_key": "rerun_required", "status_value": readiness["summary"]["rerun_required"]},
            {"status_key": "changed_artifact_count", "status_value": readiness["summary"]["changed_artifact_count"]},
            {"status_key": "nearest_candidate_sector_id", "status_value": bundle["summary"]["closest_candidate_sector_id"]},
            {"status_key": "decisive_watch_symbol", "status_value": bundle["summary"]["decisive_watch_symbol"]},
            {"status_key": "bk0808_current_v6_symbol_count", "status_value": bk0808["current_v6_symbol_count"]},
            {"status_key": "bk0808_same_plane_symbol_gap", "status_value": bk0808["same_plane_symbol_gap"]},
            {"status_key": "bk0808_board_composite_gap", "status_value": bk0808["board_composite_gap"]},
            {"status_key": "bk0808_bridge_block", "status_value": bk0808["bridge_block"]},
            {"status_key": "watch_symbol_timeline_days", "status_value": bk0808["watch_symbol_timeline_days"]},
            {"status_key": "watch_symbol_leader_core_days", "status_value": bk0808["watch_symbol_leader_core_days"]},
            {"status_key": "watch_symbol_near_surface_days", "status_value": bk0808["watch_symbol_near_surface_days"]},
            {"status_key": "watch_symbol_inactive_days", "status_value": bk0808["watch_symbol_inactive_days"]},
            {
                "status_key": "next_action",
                "status_value": "wait_for_real_v6_same_plane_emergence_of_600118_then_rerun_transfer_chain",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v131a_transfer_program_operational_status_card_v1",
            "program_status": "frozen",
            "rerun_required": readiness["summary"]["rerun_required"],
            "nearest_candidate_sector_id": bundle["summary"]["closest_candidate_sector_id"],
            "decisive_watch_symbol": bundle["summary"]["decisive_watch_symbol"],
            "authoritative_status": "operational_status_card_ready_for_do_not_rerun_posture",
            "authoritative_rule": "under_current_static_data_the_only_correct_action_is_to_monitor_the_change_gate_not_to_restart_transfer_analysis",
        }
        interpretation = [
            "V1.31A compresses the frozen transfer program into a single operational status card.",
            "This is not a new research frontier; it is an execution aid that answers three questions immediately: are we frozen, who is closest, and what exact event would justify a rerun.",
        ]
        return V131ATransferProgramOperationalStatusCardReport(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )

    def write_status_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131ATransferProgramOperationalStatusCardReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V131ATransferProgramOperationalStatusCardAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131a_transfer_program_operational_status_card_v1",
        result=result,
    )
    analyzer.write_status_csv(result.status_rows)


if __name__ == "__main__":
    main()
