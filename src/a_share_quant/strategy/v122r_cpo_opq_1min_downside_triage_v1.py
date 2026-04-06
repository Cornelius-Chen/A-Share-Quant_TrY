from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V122RCpoOpq1MinDownsideTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V122RCpoOpq1MinDownsideTriageAnalyzer:
    def analyze(self) -> V122RCpoOpq1MinDownsideTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "soft_component",
                "reason": "alive_but_too_weak_for_candidate",
                "recommended_next_step": "attach_only_as_downside_penalty_in_future_audit",
            },
            {
                "reviewer": "Tesla",
                "verdict": "explanatory_only",
                "reason": "holdout_and_timesplit_too_close_to_random",
                "recommended_next_step": "stop_family_expansion_until_labels_or_history_improve",
            },
            {
                "reviewer": "James",
                "verdict": "candidate_only",
                "reason": "discovery_gap_real_and_holdouts_above_random",
                "recommended_next_step": "triage_without_replay_or_new_family",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v122r_cpo_opq_1min_downside_triage_v1",
            "authoritative_status": "soft_component",
            "rationale": "alive_but_not_strong_enough_for_candidate_rule",
            "forbidden_next_step": "standalone_replay_promotion_or_new_1min_downside_family_expansion",
            "recommended_next_posture": "retain_as_1min_downside_soft_penalty_only",
        }
        interpretation = [
            "The new 1-minute downside failure branch is not dead, but it is not strong enough to be a candidate rule.",
            "It is best treated as a soft downside penalty rather than a standalone action branch.",
            "The correct next step is not more family expansion, but using it only as a soft component when the broader downside stack is revisited.",
        ]
        return V122RCpoOpq1MinDownsideTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122RCpoOpq1MinDownsideTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122RCpoOpq1MinDownsideTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122r_cpo_opq_1min_downside_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
