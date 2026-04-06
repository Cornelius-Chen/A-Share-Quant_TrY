from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V119YCpoVwxThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V119YCpoVwxThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v119v_payload: dict[str, Any],
        v119w_payload: dict[str, Any],
        v119x_payload: dict[str, Any],
    ) -> V119YCpoVwxThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v119y_cpo_vwx_three_run_adversarial_triage_v1",
            "triage_scope": "V119V_V119W_V119X",
            "branch_name": "limit_discipline_support_score_candidate",
            "branch_status": "explanatory_only",
            "hard_candidate_allowed": False,
            "candidate_only_allowed": False,
            "soft_expectancy_component_allowed": False,
            "explanatory_only_allowed": True,
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "authoritative_current_problem": "no_increment_over_parent_and_worse_time_split_turn_this_into_a_story_not_a_branch",
            "recommended_next_posture": "kill_as_scoring_branch_keep_only_as_explanatory_non_chase_overlay_idea_and_move_on",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "explanatory_only",
                "key_reason": "It ties the parent externally but worsens chronology, so it should not retain candidate budget.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "explanatory_only",
                "key_reason": "The line tells a cleaner non-chase story but adds no external increment and degrades time-split stability.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "candidate_only_low_priority",
                "key_reason": "There is some signal, but not enough to justify more budget beyond a low-priority reference line.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "freeze_explanatory_only_by_majority",
                "key_reason": (
                    f"Discovery gap={v119v_payload['summary']['candidate_score_mean_gap_positive_minus_negative']} vs parent "
                    f"{v119v_payload['summary']['parent_score_mean_gap_positive_minus_negative']}; "
                    f"external={v119w_payload['summary']['best_balanced_accuracy']} vs parent "
                    f"{v119w_payload['summary']['parent_best_balanced_accuracy']}; "
                    f"time-split mean/min={v119x_payload['summary']['mean_test_balanced_accuracy']}/"
                    f"{v119x_payload['summary']['min_test_balanced_accuracy']} vs parent "
                    f"{v119x_payload['summary']['parent_mean_test_balanced_accuracy']}/"
                    f"{v119x_payload['summary']['parent_min_test_balanced_accuracy']}."
                ),
            },
        ]
        interpretation = [
            "V1.19Y is the scheduled three-run adversarial review for the narrow limit-band discipline branch.",
            "The branch tells a plausible non-chase story, but the measured surface is too clear: no external gain over the parent and worse chronology.",
            "The authoritative freeze follows the reviewer majority and kills this line as a scoring branch while keeping only the explanatory idea.",
        ]
        return V119YCpoVwxThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119YCpoVwxThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119YCpoVwxThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119v_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v119v_cpo_limit_discipline_support_discovery_v1.json").read_text(
                encoding="utf-8"
            )
        ),
        v119w_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v119w_cpo_limit_discipline_support_external_audit_v1.json").read_text(
                encoding="utf-8"
            )
        ),
        v119x_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v119x_cpo_limit_discipline_support_time_split_validation_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119y_cpo_vwx_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
