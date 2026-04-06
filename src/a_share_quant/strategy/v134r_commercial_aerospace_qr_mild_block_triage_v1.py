from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134RCommercialAerospaceQRMildBlockTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134RCommercialAerospaceQRMildBlockTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134q_commercial_aerospace_broader_hit_mild_block_audit_v1.json"
        )
        self.output_csv = repo_root / "data" / "training" / "commercial_aerospace_qr_mild_block_triage_v1.csv"

    def analyze(self) -> V134RCommercialAerospaceQRMildBlockTriageReport:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        delta = float(audit["summary"]["same_day_loss_avoided_delta"])
        improvement = delta > 0

        triage_rows = [
            {
                "component": "predicted_mild_boundary_change",
                "status": "promote_inside_phase_2" if improvement else "blocked",
                "detail": (
                    f"same_day_loss_avoided_delta = {audit['summary']['same_day_loss_avoided_delta']}, "
                    f"blocked_mild_session_count = {audit['summary']['blocked_mild_session_count']}"
                ),
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "This is a local boundary tightening only and does not authorize any wider surface expansion.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "This refinement remains inside phase 2 and does not authorize replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134r_commercial_aerospace_qr_mild_block_triage_v1",
            "authoritative_status": (
                "promote_predicted_mild_block_inside_broader_hit_phase2_lane"
                if improvement
                else "keep_original_broader_hit_boundary"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34R judges whether the first boundary-tightening refinement should replace the original broader-hit widening inside phase 2.",
            "The judgment remains entirely local to phase 2 and does not alter the replay boundary.",
        ]
        return V134RCommercialAerospaceQRMildBlockTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RCommercialAerospaceQRMildBlockTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RCommercialAerospaceQRMildBlockTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134r_commercial_aerospace_qr_mild_block_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
