from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133ZCommercialAerospaceYZAllSessionVisibilityTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V133ZCommercialAerospaceYZAllSessionVisibilityTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.all_session_path = (
            repo_root / "reports" / "analysis" / "v133y_commercial_aerospace_point_in_time_all_session_feed_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_yz_all_session_visibility_triage_v1.csv"
        )

    def analyze(self) -> V133ZCommercialAerospaceYZAllSessionVisibilityTriageReport:
        all_session = json.loads(self.all_session_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "all_session_visibility_surface",
                "status": "retain_as_phase_1_terminal_surface",
                "rationale": "the six-symbol first-hour session surface now exists as the widest lawful phase-1 visibility object",
            },
            {
                "component": "phase_1_visibility_expansion",
                "status": "complete",
                "rationale": "visibility has widened from canonical seeds to broader hits to the full all-session surface",
            },
            {
                "component": "intraday_execution_simulator",
                "status": "still_blocked",
                "rationale": "the next workstream is not automatically open; simulation still depends on the frozen phase boundary in v133m/v133n",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v133z_commercial_aerospace_yz_all_session_visibility_triage_v1",
            "all_session_count": all_session["summary"]["all_session_count"],
            "seed_symbol_count": all_session["summary"]["seed_symbol_count"],
            "authoritative_status": "complete_phase_1_visibility_and_keep_intraday_execution_lane_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.33Z closes the current phase-1 visibility program by recognizing the all-session surface as the widest lawful visibility object.",
            "The simulator and replay workstreams remain blocked even after phase 1 is complete.",
        ]
        return V133ZCommercialAerospaceYZAllSessionVisibilityTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133ZCommercialAerospaceYZAllSessionVisibilityTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133ZCommercialAerospaceYZAllSessionVisibilityTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133z_commercial_aerospace_yz_all_session_visibility_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
