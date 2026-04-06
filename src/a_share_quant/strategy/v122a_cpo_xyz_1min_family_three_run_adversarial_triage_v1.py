from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V122ACpoXyz1MinFamilyThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V122ACpoXyz1MinFamilyThreeRunAdversarialTriageAnalyzer:
    def analyze(self) -> V122ACpoXyz1MinFamilyThreeRunAdversarialTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "supportive_continuation_status": "candidate_family_only",
                "burst_fade_trap_status": "candidate_family_only",
                "main_risk": "short_recent_unlabeled_window",
                "recommended_next_step": "label_aligned_audit",
            },
            {
                "reviewer": "Tesla",
                "supportive_continuation_status": "candidate_family_only",
                "burst_fade_trap_status": "candidate_family_only",
                "main_risk": "premature_rule_inference",
                "recommended_next_step": "label_aligned_audit",
            },
            {
                "reviewer": "James",
                "supportive_continuation_status": "candidate_family_only",
                "burst_fade_trap_status": "candidate_family_only",
                "main_risk": "no_action_label_alignment_yet",
                "recommended_next_step": "label_aligned_audit",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v122a_cpo_xyz_1min_family_three_run_adversarial_triage_v1",
            "supportive_continuation_status": "candidate_family_only",
            "burst_fade_trap_status": "candidate_family_only",
            "reviewer_consensus": "unanimous",
            "forbidden_next_step": "any_replay_promotion_or_shadow_replay",
            "recommended_next_posture": "run_short_horizon_label_aligned_expectancy_audit",
        }
        interpretation = [
            "All three reviewers agree the two 1-minute families are worth keeping but only as non-replay candidate families.",
            "All three reviewers agree the next required step is label-aligned audit rather than more geometry or replay.",
            "This preserves the 1-minute line without repeating the earlier mistake of promoting structure before evidence.",
        ]
        return V122ACpoXyz1MinFamilyThreeRunAdversarialTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122ACpoXyz1MinFamilyThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122ACpoXyz1MinFamilyThreeRunAdversarialTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122a_cpo_xyz_1min_family_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
