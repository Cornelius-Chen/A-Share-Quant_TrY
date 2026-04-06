from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134PCommercialAerospaceNOPBroaderHitDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134PCommercialAerospaceNOPBroaderHitDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.attr_path = analysis_dir / "v134n_commercial_aerospace_broader_hit_simulator_attribution_v1.json"
        self.fail_path = analysis_dir / "v134o_commercial_aerospace_broader_hit_supervision_failure_review_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_nop_broader_hit_direction_triage_v1.csv"
        )

    def analyze(self) -> V134PCommercialAerospaceNOPBroaderHitDirectionTriageReport:
        attr = json.loads(self.attr_path.read_text(encoding="utf-8"))
        failure = json.loads(self.fail_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "broader_hit_widening_value",
                "status": "retain_with_refinement",
                "detail": (
                    f"same_day_loss_avoided_total = {attr['summary']['same_day_loss_avoided_total']}, "
                    f"best_tier = {attr['summary']['best_tier']}"
                ),
            },
            {
                "component": "predicted_mild_session_execution",
                "status": "tighten_next",
                "detail": failure["summary"]["recommended_boundary_change"],
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "Broader-hit supervision remains useful, but it is not clean enough to justify all-session widening.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "The broader-hit branch remains a phase-2 shadow object and still cannot bind into replay.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134p_commercial_aerospace_nop_broader_hit_direction_triage_v1",
            "authoritative_status": "retain_broader_hit_phase2_lane_but_tighten_predicted_mild_execution_boundary_next",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34P converts the wider phase-2 supervision review into the next direction judgment.",
            "The wider lane is still worth keeping, but its next optimization is boundary tightening rather than another expansion step.",
        ]
        return V134PCommercialAerospaceNOPBroaderHitDirectionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PCommercialAerospaceNOPBroaderHitDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PCommercialAerospaceNOPBroaderHitDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134p_commercial_aerospace_nop_broader_hit_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
