from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134YCommercialAerospaceXYLocalClusterDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134YCommercialAerospaceXYLocalClusterDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134x_commercial_aerospace_reversal_late_severe_block_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_xy_local_cluster_direction_triage_v1.csv"
        )

    def analyze(self) -> V134YCommercialAerospaceXYLocalClusterDirectionTriageReport:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        improvement = float(audit["summary"]["same_day_loss_avoided_delta"]) > 0

        triage_rows = [
            {
                "component": "reversal_late_severe_block",
                "status": "promote_inside_current_wider_reference" if improvement else "blocked",
                "detail": (
                    f"impacted_session_count = {audit['summary']['impacted_session_count']}, "
                    f"same_day_loss_avoided_delta = {audit['summary']['same_day_loss_avoided_delta']}"
                ),
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "This is a local cluster refinement only and does not change the surface boundary.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "The local cluster refinement remains a phase-2 shadow improvement only.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134y_commercial_aerospace_xy_local_cluster_direction_triage_v1",
            "authoritative_status": (
                "promote_reversal_late_severe_block_inside_current_wider_reference"
                if improvement
                else "retain_current_wider_reference_without_local_cluster_change"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34Y turns the local failure-cluster audit into the next direction judgment.",
            "If the only remaining negative cluster is improved by blocking very-late severe on reversal-predicted sessions, that change should be promoted locally without reopening the wider surface.",
        ]
        return V134YCommercialAerospaceXYLocalClusterDirectionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134YCommercialAerospaceXYLocalClusterDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134YCommercialAerospaceXYLocalClusterDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134y_commercial_aerospace_xy_local_cluster_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
