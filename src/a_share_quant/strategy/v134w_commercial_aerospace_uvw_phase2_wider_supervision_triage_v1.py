from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134WCommercialAerospaceUVWPhase2WiderSupervisionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134WCommercialAerospaceUVWPhase2WiderSupervisionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.attr_path = analysis_dir / "v134u_commercial_aerospace_phase2_wider_reference_attribution_v1.json"
        self.fail_path = analysis_dir / "v134v_commercial_aerospace_phase2_wider_failure_cluster_review_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_uvw_phase2_wider_supervision_triage_v1.csv"
        )

    def analyze(self) -> V134WCommercialAerospaceUVWPhase2WiderSupervisionTriageReport:
        attr = json.loads(self.attr_path.read_text(encoding="utf-8"))
        fail = json.loads(self.fail_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "current_wider_reference",
                "status": "retain",
                "detail": (
                    f"same_day_loss_avoided_total = {attr['summary']['same_day_loss_avoided_total']}, "
                    f"best_symbol = {attr['summary']['best_symbol']}"
                ),
            },
            {
                "component": "failure_shape",
                "status": "concentrated_enough_for_local_supervision",
                "detail": (
                    f"negative_session_count = {fail['summary']['negative_session_count']}, "
                    f"top_failure_cluster = {fail['summary']['top_failure_cluster']}"
                ),
            },
            {
                "component": "next_optimization_direction",
                "status": "supervise_local_clusters",
                "detail": "The next step should stay inside the current wider reference and inspect the top failure cluster before any further widening.",
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "The branch still does not have a reason to leave the bounded broader-hit surface.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "Nothing in the current wider supervision review authorizes replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134w_commercial_aerospace_uvw_phase2_wider_supervision_triage_v1",
            "authoritative_status": "retain_current_wider_reference_and_shift_next_to_local_failure_cluster_supervision",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34W converts the wider-reference attribution and failure clustering into the next direction judgment.",
            "The branch should now deepen supervision within the current wider reference instead of opening a new surface.",
        ]
        return V134WCommercialAerospaceUVWPhase2WiderSupervisionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134WCommercialAerospaceUVWPhase2WiderSupervisionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134WCommercialAerospaceUVWPhase2WiderSupervisionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134w_commercial_aerospace_uvw_phase2_wider_supervision_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
