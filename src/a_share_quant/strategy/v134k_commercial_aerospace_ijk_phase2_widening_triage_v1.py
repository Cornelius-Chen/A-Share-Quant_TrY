from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134KCommercialAerospaceIJKPhase2WideningTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KCommercialAerospaceIJKPhase2WideningTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.review_path = analysis_dir / "v134i_commercial_aerospace_phase2_seed_supervision_review_v1.json"
        self.protocol_path = analysis_dir / "v134j_commercial_aerospace_phase2_broader_hit_widening_protocol_v1.json"
        self.output_csv = repo_root / "data" / "training" / "commercial_aerospace_ijk_phase2_widening_triage_v1.csv"

    def analyze(self) -> V134KCommercialAerospaceIJKPhase2WideningTriageReport:
        review = json.loads(self.review_path.read_text(encoding="utf-8"))
        protocol = json.loads(self.protocol_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "phase2_seed_training_result",
                "status": "reasonable",
                "detail": review["summary"]["phase2_supervision_verdict"],
            },
            {
                "component": "broader_hit_widening",
                "status": "approved_with_guardrails",
                "detail": (
                    f"allowed_surface = {protocol['summary']['allowed_widening_surface']}, "
                    f"allowed_execution_tiers = {', '.join(protocol['summary']['allowed_execution_tiers'])}"
                ),
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "Do not jump from six seeds to the full all-session surface; widen only to the already-flagged broader-hit sessions first.",
            },
            {
                "component": "mild_execution_promotion",
                "status": "blocked",
                "detail": "mild_override_watch remains governance-only and is not promotable into an execution sell tier.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "No replay binding is authorized by the current phase-2 supervision review or widening protocol.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134k_commercial_aerospace_ijk_phase2_widening_triage_v1",
            "authoritative_status": "approve_broader_hit_phase2_widening_with_guardrails_but_keep_all_session_and_replay_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34K is the direction judgment after supervising the current phase-2 seed training outputs.",
            "The branch is now mature enough to widen once, but only to the already-flagged broader-hit sessions and only with reversal/severe execution tiers under the same intraday simulator clock.",
        ]
        return V134KCommercialAerospaceIJKPhase2WideningTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KCommercialAerospaceIJKPhase2WideningTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KCommercialAerospaceIJKPhase2WideningTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134k_commercial_aerospace_ijk_phase2_widening_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
