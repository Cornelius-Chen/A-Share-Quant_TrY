from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133XCommercialAerospaceWXBroaderVisibilityTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V133XCommercialAerospaceWXBroaderVisibilityTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v133w_commercial_aerospace_point_in_time_broader_visibility_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_wx_broader_visibility_triage_v1.csv"
        )

    def analyze(self) -> V133XCommercialAerospaceWXBroaderVisibilityTriageReport:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        summary = audit["summary"]
        all_zero = (
            summary["same_bar_violation_count"] == 0
            and summary["path_cutoff_violation_count"] == 0
            and summary["lineage_monotonic_violation_count"] == 0
            and summary["event_visibility_violation_count"] == 0
            and summary["warmup_nonnull_violation_count"] == 0
        )

        triage_rows = [
            {
                "component": "broader_hit_visibility_surface",
                "status": "accepted_as_phase_1_broader_surface" if all_zero else "blocked",
                "rationale": "the broader 24-session surface passes the same point-in-time legality checks as the canonical seed surface",
            },
            {
                "component": "all_session_visibility_expansion",
                "status": "next_allowed_move" if all_zero else "blocked",
                "rationale": "the next lawful expansion is from the broader hit surface to a still-wider minute visibility surface, not to simulation",
            },
            {
                "component": "intraday_execution_simulator",
                "status": "still_blocked",
                "rationale": "passing broader visibility audits still does not satisfy the separate simulator or replay-lane prerequisites",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        report_summary = {
            "acceptance_posture": "freeze_v133x_commercial_aerospace_wx_broader_visibility_triage_v1",
            "broader_hit_session_count": summary["broader_hit_session_count"],
            "authoritative_status": "accept_broader_phase_1_visibility_surface_and_keep_execution_lane_blocked" if all_zero else "block_broader_phase_1_surface",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.33X converts the broader visibility audit into a direction decision for the next lawful expansion inside phase 1.",
            "The branch may widen visibility further, but simulation and replay remain explicitly closed.",
        ]
        return V133XCommercialAerospaceWXBroaderVisibilityTriageReport(
            summary=report_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133XCommercialAerospaceWXBroaderVisibilityTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133XCommercialAerospaceWXBroaderVisibilityTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133x_commercial_aerospace_wx_broader_visibility_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
