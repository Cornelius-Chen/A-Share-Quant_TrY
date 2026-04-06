from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V122GCpoDef1MinFamilyTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V122GCpoDef1MinFamilyTriageAnalyzer:
    def analyze(self) -> V122GCpoDef1MinFamilyTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "burst_fade_trap_status": "dead",
                "supportive_continuation_quality_score_status": "explanatory_only",
                "recommended_next_step": "stop_1min_family_scoring_and_move_to_action_timepoint_labels",
            },
            {
                "reviewer": "Tesla",
                "burst_fade_trap_status": "dead",
                "supportive_continuation_quality_score_status": "dead",
                "recommended_next_step": "stop_current_1min_discovery_until_data_or_labels_improve",
            },
            {
                "reviewer": "James",
                "burst_fade_trap_status": "dead",
                "supportive_continuation_quality_score_status": "explanatory_only",
                "recommended_next_step": "rebuild_1min_action_timepoint_label_base",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v122g_cpo_def_1min_family_triage_v1",
            "burst_fade_trap_status": "dead",
            "supportive_continuation_family_status": "candidate_family_only",
            "supportive_continuation_quality_score_status": "explanatory_only",
            "reviewer_consensus_on_burst_fade_trap": "unanimous_dead",
            "reviewer_majority_on_quality_score": "explanatory_only",
            "forbidden_next_step": "any_replay_promotion_or_further_same_family_score_tuning",
            "recommended_next_posture": "build_stricter_1min_action_timepoint_label_base",
        }
        interpretation = [
            "The burst-fade trap family is dead and should not receive more resources.",
            "The supportive continuation family itself remains alive, but its first quality-score hardening attempt failed chronology and is downgraded to explanatory only.",
            "The next step is not more family scoring, but a stricter 1-minute action-timepoint label base.",
        ]
        return V122GCpoDef1MinFamilyTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122GCpoDef1MinFamilyTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122GCpoDef1MinFamilyTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122g_cpo_def_1min_family_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
