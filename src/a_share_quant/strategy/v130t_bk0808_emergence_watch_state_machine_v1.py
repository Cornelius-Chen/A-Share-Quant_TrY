from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130TBK0808EmergenceWatchStateMachineReport:
    summary: dict[str, Any]
    state_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "state_rows": self.state_rows,
            "interpretation": self.interpretation,
        }


class V130TBK0808EmergenceWatchStateMachineAnalyzer:
    TARGET_SYMBOL = "600118"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.watch_window_path = repo_root / "reports" / "analysis" / "v130r_bk0808_600118_near_surface_watch_window_audit_v1.json"
        self.trigger_path = repo_root / "reports" / "analysis" / "v130p_bk0808_second_symbol_emergence_trigger_protocol_v1.json"
        self.output_csv_path = repo_root / "data" / "training" / "bk0808_emergence_watch_state_machine_v1.csv"

    def analyze(self) -> V130TBK0808EmergenceWatchStateMachineReport:
        watch_window_report = json.loads(self.watch_window_path.read_text(encoding="utf-8"))
        trigger_report = json.loads(self.trigger_path.read_text(encoding="utf-8"))
        trigger_row = next(row for row in trigger_report["trigger_rows"] if row["symbol"] == self.TARGET_SYMBOL)

        state_rows: list[dict[str, Any]] = []
        for row in watch_window_report["watch_rows"]:
            if row["near_surface_watch_active"]:
                watch_state = "near_surface_watch"
            else:
                watch_state = "inactive_watch"

            if row["near_surface_watch_active"] and trigger_row["reopen_candidate_if_emerged"]:
                next_state_if_emerged = "reopen_candidate"
            elif row["near_surface_watch_active"]:
                next_state_if_emerged = "watch_only"
            else:
                next_state_if_emerged = "no_change"

            state_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "watch_state": watch_state,
                    "assignment_layer": row["assignment_layer"],
                    "assignment_score": row["assignment_score"],
                    "board_composite": row["board_composite"],
                    "near_surface_watch_active": row["near_surface_watch_active"],
                    "same_plane_support_present": False,
                    "next_state_if_emerged": next_state_if_emerged,
                }
            )

        near_surface_count = sum(row["watch_state"] == "near_surface_watch" for row in state_rows)
        summary = {
            "acceptance_posture": "freeze_v130t_bk0808_emergence_watch_state_machine_v1",
            "symbol": self.TARGET_SYMBOL,
            "total_observed_days": len(state_rows),
            "near_surface_watch_day_count": near_surface_count,
            "inactive_watch_day_count": len(state_rows) - near_surface_count,
            "current_same_plane_support_present": False,
            "current_reopen_candidate_state": False,
            "authoritative_status": "bk0808_watch_state_machine_operational_but_worker_still_frozen",
            "authoritative_rule": "600118_may_progress_from_inactive_to_near_surface_watch_but_cannot_promote_bk0808_until_real_v6_same_plane_support_exists",
        }
        interpretation = [
            "V1.30T converts the BK0808 watch evidence into an explicit two-state monitoring machine: inactive watch versus near-surface watch.",
            "The machine is intentionally conservative: without real v6 same-plane support, BK0808 never enters a live reopen-candidate state.",
        ]
        return V130TBK0808EmergenceWatchStateMachineReport(
            summary=summary,
            state_rows=state_rows,
            interpretation=interpretation,
        )

    def write_state_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(*, reports_dir: Path, report_name: str, result: V130TBK0808EmergenceWatchStateMachineReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V130TBK0808EmergenceWatchStateMachineAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130t_bk0808_emergence_watch_state_machine_v1",
        result=result,
    )
    analyzer.write_state_csv(result.state_rows)


if __name__ == "__main__":
    main()
