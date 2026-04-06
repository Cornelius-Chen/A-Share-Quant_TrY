from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V119OCpoLmnThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V119OCpoLmnThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v119l_payload: dict[str, Any],
        v119m_payload: dict[str, Any],
        v119n_payload: dict[str, Any],
    ) -> V119OCpoLmnThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v119o_cpo_lmn_three_run_adversarial_triage_v1",
            "triage_scope": "V119L_V119M_V119N",
            "branch_name": "participation_turnover_elg_support_score_candidate",
            "branch_status": "hard_candidate_non_replay_only",
            "hard_candidate_allowed": True,
            "candidate_only_allowed": True,
            "soft_expectancy_component_allowed": False,
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "authoritative_current_problem": "still_needs_one_non_replay_cycle_before_any_execution_surface_but_no_longer_deserves_candidate_only_language",
            "recommended_next_posture": "retain_as_first_non_replay_hard_candidate_and_continue_one_more_non_replay_audit_cycle_before_any_replay_consideration",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "candidate_only",
                "key_reason": "The branch is materially stronger than HIJ but should still clear one more adversarial cycle before hard-candidate language is frozen.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "hard_candidate_non_replay_only",
                "key_reason": "External and chronology surfaces are now strong enough to upgrade the branch beyond candidate-only while still blocking replay-facing use.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "hard_candidate_non_replay_only",
                "key_reason": "This is the strongest live CPO line so far and already deserves hard-candidate language, but replay remains premature.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "hard_candidate_consensus_majority_non_replay_only",
                "key_reason": (
                    f"V119L gap={v119l_payload['summary']['candidate_score_mean_gap_positive_minus_negative']}, "
                    f"V119M best_bal_acc={v119m_payload['summary']['best_balanced_accuracy']}, "
                    f"V119N mean/min_test_bal_acc={v119n_payload['summary']['mean_test_balanced_accuracy']}/{v119n_payload['summary']['min_test_balanced_accuracy']}."
                ),
            },
        ]
        interpretation = [
            "V1.19O is the scheduled three-run adversarial review for the ELG-supported participation-turnover combo branch.",
            "The reviewers agree the branch is materially stronger than the prior HIJ combo; the only disagreement is whether to stay candidate-only for one more cycle or already admit hard-candidate language.",
            "The authoritative freeze accepts the majority view: this becomes the first non-replay hard candidate in the current CPO intraday quality-side program, while replay and shadow replay remain blocked.",
        ]
        return V119OCpoLmnThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119OCpoLmnThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119OCpoLmnThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119l_payload=json.loads((repo_root / "reports" / "analysis" / "v119l_cpo_participation_turnover_elg_support_discovery_v1.json").read_text(encoding="utf-8")),
        v119m_payload=json.loads((repo_root / "reports" / "analysis" / "v119m_cpo_participation_turnover_elg_support_external_audit_v1.json").read_text(encoding="utf-8")),
        v119n_payload=json.loads((repo_root / "reports" / "analysis" / "v119n_cpo_participation_turnover_elg_support_time_split_validation_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119o_cpo_lmn_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
