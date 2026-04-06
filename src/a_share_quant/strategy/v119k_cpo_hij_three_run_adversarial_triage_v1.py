from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V119KCpoHijThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V119KCpoHijThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v119h_payload: dict[str, Any],
        v119i_payload: dict[str, Any],
        v119j_payload: dict[str, Any],
    ) -> V119KCpoHijThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v119k_cpo_hij_three_run_adversarial_triage_v1",
            "triage_scope": "V119H_V119I_V119J",
            "branch_name": "participation_turnover_combo_score_candidate",
            "branch_status": "candidate_only",
            "hard_candidate_allowed": False,
            "candidate_only_allowed": True,
            "soft_expectancy_component_allowed": False,
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "authoritative_current_problem": "improved_but_not_closed_2024_holdout_recall_hole_despite_best_so_far_chronology_surface",
            "recommended_next_posture": "continue_one_more_non_replay_audit_cycle_on_2024_holdout_failure_surface_without_expanding_into_replay",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "candidate_only",
                "key_reason": "The combo is materially stronger than either component alone, but the remaining 2024 positive-recall hole still blocks hard-candidate promotion.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "candidate_only",
                "key_reason": "This is the cleanest current non-replay quality-side line, yet replay-facing use would still be premature while one year bucket remains structurally weak.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "hard_candidate_but_non_replay_only",
                "key_reason": "The combo already looks like a hard candidate in principle because the external and chronology surface beat the single branches, but replay must still stay blocked.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "candidate_only_consensus_floor",
                "key_reason": (
                    f"V119H gap={v119h_payload['summary']['candidate_score_mean_gap_positive_minus_negative']}, "
                    f"V119I best_bal_acc={v119i_payload['summary']['best_balanced_accuracy']}, "
                    f"V119J mean/min_test_bal_acc={v119j_payload['summary']['mean_test_balanced_accuracy']}/{v119j_payload['summary']['min_test_balanced_accuracy']}."
                ),
            },
        ]
        interpretation = [
            "V1.19K is the scheduled three-run adversarial review for the participation-turnover combo branch.",
            "All reviewers agree the combo is stronger than the standalone participation and turnover-discipline branches; the live disagreement is whether that strength already warrants hard-candidate language.",
            "The authoritative freeze stays conservative: retain the branch as candidate-only, block replay and shadow replay, and spend one more non-replay cycle on the unresolved 2024 holdout weakness.",
        ]
        return V119KCpoHijThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119KCpoHijThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119KCpoHijThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119h_payload=json.loads((repo_root / "reports" / "analysis" / "v119h_cpo_participation_turnover_combo_discovery_v1.json").read_text(encoding="utf-8")),
        v119i_payload=json.loads((repo_root / "reports" / "analysis" / "v119i_cpo_participation_turnover_combo_external_audit_v1.json").read_text(encoding="utf-8")),
        v119j_payload=json.loads((repo_root / "reports" / "analysis" / "v119j_cpo_participation_turnover_combo_time_split_validation_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119k_cpo_hij_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
