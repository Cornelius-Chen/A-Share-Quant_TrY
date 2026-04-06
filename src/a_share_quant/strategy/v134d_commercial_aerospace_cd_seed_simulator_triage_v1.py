from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134DCommercialAerospaceCDSeedSimulatorTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134DCommercialAerospaceCDSeedSimulatorTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.sim_path = (
            repo_root / "reports" / "analysis" / "v134c_commercial_aerospace_intraday_seed_simulator_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_cd_seed_simulator_triage_v1.csv"
        )

    def analyze(self) -> V134DCommercialAerospaceCDSeedSimulatorTriageReport:
        sim = json.loads(self.sim_path.read_text(encoding="utf-8"))
        summary = sim["summary"]

        triage_rows = [
            {
                "component": "seed_shadow_simulator",
                "status": "retain_as_phase_2_seed_surface",
                "detail": "the first canonical-seed simulator exists and respects next-bar-open execution timing",
            },
            {
                "component": "same_bar_execution_boundary",
                "status": "accepted",
                "detail": "all seed fills occur on trigger_minute + 1 with no same-bar execution exception",
            },
            {
                "component": "first_hour_horizon_limit",
                "status": "explicitly_bounded",
                "detail": f"pending_out_of_window_count = {summary['pending_out_of_window_count']}",
            },
            {
                "component": "phase_3_replay_lane",
                "status": "still_blocked",
                "detail": "seed simulation does not authorize binding into a separate intraday replay lane yet",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        report_summary = {
            "acceptance_posture": "freeze_v134d_commercial_aerospace_cd_seed_simulator_triage_v1",
            "simulated_order_count": summary["simulated_order_count"],
            "pending_out_of_window_count": summary["pending_out_of_window_count"],
            "authoritative_status": "retain_phase_2_seed_simulator_but_keep_replay_lane_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34D converts the first seed-session intraday simulator run into a governance triage result.",
            "The branch may keep building inside phase 2, but replay binding remains blocked and the first-hour horizon limit must stay explicit.",
        ]
        return V134DCommercialAerospaceCDSeedSimulatorTriageReport(
            summary=report_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134DCommercialAerospaceCDSeedSimulatorTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134DCommercialAerospaceCDSeedSimulatorTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134d_commercial_aerospace_cd_seed_simulator_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
