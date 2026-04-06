from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130VTransferProgramGovernanceBundleReport:
    summary: dict[str, Any]
    bundle_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "bundle_rows": self.bundle_rows,
            "interpretation": self.interpretation,
        }


class V130VTransferProgramGovernanceBundleAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.monitor_path = repo_root / "reports" / "analysis" / "v130k_transfer_program_watch_monitor_snapshot_v1.json"
        self.bk0808_trigger_path = repo_root / "reports" / "analysis" / "v130p_bk0808_second_symbol_emergence_trigger_protocol_v1.json"
        self.bk0808_state_path = repo_root / "reports" / "analysis" / "v130t_bk0808_emergence_watch_state_machine_v1.json"
        self.bk0808_triage_path = repo_root / "reports" / "analysis" / "v130u_bk0808_tu_emergence_state_governance_triage_v1.json"
        self.output_csv_path = repo_root / "data" / "training" / "transfer_program_governance_bundle_v1.csv"

    def analyze(self) -> V130VTransferProgramGovernanceBundleReport:
        monitor_report = json.loads(self.monitor_path.read_text(encoding="utf-8"))
        trigger_report = json.loads(self.bk0808_trigger_path.read_text(encoding="utf-8"))
        state_report = json.loads(self.bk0808_state_path.read_text(encoding="utf-8"))
        triage_report = json.loads(self.bk0808_triage_path.read_text(encoding="utf-8"))

        bundle_rows: list[dict[str, Any]] = []
        for row in monitor_report["monitor_rows"]:
            if row["sector_id"] == "BK0808":
                trigger_row = trigger_report["trigger_rows"][0]
                bundle_rows.append(
                    {
                        "sector_id": row["sector_id"],
                        "monitor_role": "nearest_reopen_candidate_under_freeze",
                        "current_v6_symbol_count": row["current_v6_symbol_count"],
                        "same_plane_symbol_gap": row["same_plane_symbol_gap"],
                        "board_composite_gap": row["board_composite_gap"],
                        "bridge_block": row["bridge_only_or_not_ready"],
                        "reopen_ready": row["reopen_ready"],
                        "decisive_watch_symbol": trigger_row["symbol"],
                        "watch_symbol_timeline_days": trigger_row["timeline_approval_days"],
                        "watch_symbol_leader_core_days": trigger_row["timeline_leader_core_days"],
                        "watch_symbol_current_v6_snapshot_days": trigger_row["current_v6_snapshot_days"],
                        "watch_symbol_near_surface_days": state_report["summary"]["near_surface_watch_day_count"],
                        "watch_symbol_inactive_days": state_report["summary"]["inactive_watch_day_count"],
                        "governance_state": triage_report["summary"]["authoritative_status"],
                        "next_action_rule": "reopen_only_after_real_v6_same_plane_emergence_of_600118",
                    }
                )
            else:
                bundle_rows.append(
                    {
                        "sector_id": row["sector_id"],
                        "monitor_role": "secondary_frozen_candidate",
                        "current_v6_symbol_count": row["current_v6_symbol_count"],
                        "same_plane_symbol_gap": row["same_plane_symbol_gap"],
                        "board_composite_gap": row["board_composite_gap"],
                        "bridge_block": row["bridge_only_or_not_ready"],
                        "reopen_ready": row["reopen_ready"],
                        "decisive_watch_symbol": None,
                        "watch_symbol_timeline_days": None,
                        "watch_symbol_leader_core_days": None,
                        "watch_symbol_current_v6_snapshot_days": None,
                        "watch_symbol_near_surface_days": None,
                        "watch_symbol_inactive_days": None,
                        "governance_state": "frozen_watchlist_only",
                        "next_action_rule": "wait_for_multi_symbol_v6_same_plane_support",
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v130v_transfer_program_governance_bundle_v1",
            "candidate_board_count": len(bundle_rows),
            "reopen_ready_count": sum(1 for row in bundle_rows if row["reopen_ready"]),
            "closest_candidate_sector_id": "BK0808",
            "decisive_watch_symbol": "600118",
            "authoritative_status": "transfer_program_governance_bundle_frozen_but_operational",
            "authoritative_rule": "the_program_stays_frozen_but_the_monitoring_stack_is_now_complete_enough_to_tell_exactly_what_new_local_evidence_would_unlock_bk0808",
        }
        interpretation = [
            "V1.30V bundles the transfer freeze, the BK0808 trigger logic, and the BK0808 watch state machine into one governance surface.",
            "This is meant to stop repeated re-analysis under static data: until new local same-plane evidence appears, the correct posture is monitoring, not worker creation.",
        ]
        return V130VTransferProgramGovernanceBundleReport(
            summary=summary,
            bundle_rows=bundle_rows,
            interpretation=interpretation,
        )

    def write_bundle_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(*, reports_dir: Path, report_name: str, result: V130VTransferProgramGovernanceBundleReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V130VTransferProgramGovernanceBundleAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130v_transfer_program_governance_bundle_v1",
        result=result,
    )
    analyzer.write_bundle_csv(result.bundle_rows)


if __name__ == "__main__":
    main()
