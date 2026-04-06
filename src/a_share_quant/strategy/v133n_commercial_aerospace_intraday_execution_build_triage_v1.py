from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133NCommercialAerospaceIntradayExecutionBuildTriageReport:
    summary: dict[str, Any]
    review_rows: list[dict[str, Any]]
    consensus_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "review_rows": self.review_rows,
            "consensus_rows": self.consensus_rows,
            "interpretation": self.interpretation,
        }


class V133NCommercialAerospaceIntradayExecutionBuildTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.protocol_path = (
            repo_root / "reports" / "analysis" / "v133m_commercial_aerospace_intraday_execution_build_protocol_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_execution_build_triage_v1.csv"
        )

    def analyze(self) -> V133NCommercialAerospaceIntradayExecutionBuildTriageReport:
        protocol = json.loads(self.protocol_path.read_text(encoding="utf-8"))

        review_rows = [
            {
                "reviewer": "Pasteur",
                "focus": "legality_and_leakage",
                "verdict": "revise",
                "hard_point": "day-level events converted into minute-visible state updates need first_visible_ts and close-bar activation discipline",
            },
            {
                "reviewer": "Sagan",
                "focus": "engineering_sequence",
                "verdict": "sequencing_sound",
                "hard_point": "point_in_time_intraday_visibility is the hardest blocker and must stay first",
            },
            {
                "reviewer": "Dirac",
                "focus": "governance_alignment",
                "verdict": "aligned",
                "hard_point": "shadow lane must remain read-only relative to the frozen EOD primary",
            },
        ]

        consensus_rows = [
            {
                "consensus_item": "overall_direction",
                "status": "approved_with_guardrails",
                "detail": "the three-workstream order is correct and remains aligned with the frozen EOD primary posture",
            },
            {
                "consensus_item": "required_guardrail_1",
                "status": "mandatory",
                "detail": "add first_visible_ts and close-bar activation semantics before any minute-state feed is considered lawful",
            },
            {
                "consensus_item": "required_guardrail_2",
                "status": "mandatory",
                "detail": "enforce a one-way read-only boundary so the intraday shadow lane cannot mutate or back-propagate into the frozen EOD primary",
            },
            {
                "consensus_item": "next_action",
                "status": "phase_1_only",
                "detail": "begin only phase_1_visibility buildout after the two guardrails are hard-coded; do not jump ahead to simulator or replay binding",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(consensus_rows[0].keys()))
            writer.writeheader()
            writer.writerows(consensus_rows)

        summary = {
            "acceptance_posture": "freeze_v133n_commercial_aerospace_intraday_execution_build_triage_v1",
            "reviewer_count": len(review_rows),
            "consensus_count": len(consensus_rows),
            "protocol_workstream_count": protocol["summary"]["workstream_count"],
            "authoritative_status": "approve_intraday_execution_build_direction_with_guardrails_and_phase_1_only_start",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.33N converts the three-subagent review into an explicit triage result for the intraday execution build protocol.",
            "The direction is approved, but only with hard point-in-time visibility and read-only isolation guardrails in place.",
        ]
        return V133NCommercialAerospaceIntradayExecutionBuildTriageReport(
            summary=summary,
            review_rows=review_rows,
            consensus_rows=consensus_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133NCommercialAerospaceIntradayExecutionBuildTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133NCommercialAerospaceIntradayExecutionBuildTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133n_commercial_aerospace_intraday_execution_build_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
