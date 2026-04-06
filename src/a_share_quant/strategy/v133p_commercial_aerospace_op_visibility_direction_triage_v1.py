from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133PCommercialAerospaceOPVisibilityDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V133PCommercialAerospaceOPVisibilityDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.spec_path = (
            repo_root / "reports" / "analysis" / "v133o_commercial_aerospace_point_in_time_visibility_spec_v1.json"
        )
        self.protocol_path = (
            repo_root / "reports" / "analysis" / "v133m_commercial_aerospace_intraday_execution_build_protocol_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_op_visibility_direction_triage_v1.csv"
        )

    def analyze(self) -> V133PCommercialAerospaceOPVisibilityDirectionTriageReport:
        spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        protocol = json.loads(self.protocol_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "phase_1_visibility_spec",
                "status": "approved_for_implementation",
                "rationale": "the spec now hard-codes first_visible_ts, close-bar activation, and shadow-only boundaries",
            },
            {
                "component": "phase_2_simulation_surface",
                "status": "blocked_until_phase_1_audit_passes",
                "rationale": "simulator work is premature until the point-in-time feed can reconstruct canonical seed sessions without leakage",
            },
            {
                "component": "phase_3_replay_lane",
                "status": "blocked_until_phase_2_exists",
                "rationale": "replay binding remains downstream and must not be reopened before visibility and simulator infrastructure exist",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v133p_commercial_aerospace_op_visibility_direction_triage_v1",
            "protocol_phase_count": protocol["summary"]["sequencing_phase_count"],
            "visibility_spec_column_count": spec["summary"]["feed_column_count"],
            "authoritative_status": "start_phase_1_visibility_only_and_keep_later_phases_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.33P converts the visibility specification into an explicit start/stop decision for the intraday build chain.",
            "Only phase_1_visibility should move now; later phases remain blocked by design.",
        ]
        return V133PCommercialAerospaceOPVisibilityDirectionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133PCommercialAerospaceOPVisibilityDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133PCommercialAerospaceOPVisibilityDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133p_commercial_aerospace_op_visibility_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
