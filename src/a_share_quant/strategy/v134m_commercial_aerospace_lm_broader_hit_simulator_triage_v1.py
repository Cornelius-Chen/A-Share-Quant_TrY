from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134MCommercialAerospaceLMBroaderHitSimulatorTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134MCommercialAerospaceLMBroaderHitSimulatorTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.sim_path = analysis_dir / "v134l_commercial_aerospace_intraday_broader_hit_simulator_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_lm_broader_hit_simulator_triage_v1.csv"
        )

    def analyze(self) -> V134MCommercialAerospaceLMBroaderHitSimulatorTriageReport:
        sim = json.loads(self.sim_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "broader_hit_phase2_widening",
                "status": "retained_inside_phase_2",
                "detail": (
                    f"broader_hit_session_count = {sim['summary']['broader_hit_session_count']}, "
                    f"simulated_order_count = {sim['summary']['simulated_order_count']}"
                ),
            },
            {
                "component": "mild_execution_boundary",
                "status": "preserved",
                "detail": "mild remains non-executable inside broader-hit widening.",
            },
            {
                "component": "replay_boundary",
                "status": "still_blocked",
                "detail": "The broader-hit simulator is still a normalized shadow object, not a replay lane.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134m_commercial_aerospace_lm_broader_hit_simulator_triage_v1",
            "authoritative_status": "retain_broader_hit_widening_inside_phase_2_but_keep_replay_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34M judges the first broader-hit widening result.",
            "The wider simulator is retained as a phase-2 shadow object only; it still does not authorize replay binding or all-session expansion.",
        ]
        return V134MCommercialAerospaceLMBroaderHitSimulatorTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134MCommercialAerospaceLMBroaderHitSimulatorTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MCommercialAerospaceLMBroaderHitSimulatorTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134m_commercial_aerospace_lm_broader_hit_simulator_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
