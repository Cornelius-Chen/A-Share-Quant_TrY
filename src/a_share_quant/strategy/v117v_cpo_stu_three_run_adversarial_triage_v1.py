from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class V117VCpoStuThreeRunAdversarialTriageReport:
    summary: dict[str, object]
    triage_rows: list[dict[str, object]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V117VCpoStuThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v117s_payload: dict[str, object],
        v117t_payload: dict[str, object],
        v117u_payload: dict[str, object],
    ) -> V117VCpoStuThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v117v_cpo_stu_three_run_adversarial_triage_v1",
            "triage_scope": "V117S_V117T_V117U",
            "cooling_reacceleration_branch_status": "retain_candidate_only_continue_one_more_non_replay_audit_cycle",
            "promotion_allowed": False,
            "replay_facing_expansion_allowed": False,
            "mainline_investment_allowed": False,
            "candidate_only_allowed": True,
            "authoritative_current_problem": "false_positive_control_and_time_split_stability_for_cooling_reacceleration",
            "recommended_next_posture": "keep_candidate_only_and_run_one_more_non_replay_quality_audit_cycle_before_any_further_mainline_commitment",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "better_than_breakout_damage_but_not_mainline_ready",
                "key_reason": "The branch survives broader external audit better than breakout-damage, but time-split instability still blocks mainline promotion.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "real_new_semantic_axis_with_false_positive_overhang",
                "key_reason": "This is a genuinely new cooling-then-reaccelerate semantics, yet it still admits too many negative rows on the broader add pool.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "candidate_only_not_replay_facing",
                "key_reason": "There is enough learnability to keep the branch alive, but not enough robustness to justify replay-facing work.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "continue_one_more_candidate_cycle_only",
                "key_reason": (
                    f"V117T external_clear={v117t_payload['summary']['external_pool_signal_clear']}, "
                    f"V117T best_bal_acc={v117t_payload['summary']['best_balanced_accuracy']}, "
                    f"V117U min_test_bal_acc={v117u_payload['summary']['min_test_balanced_accuracy']}."
                ),
            },
        ]
        interpretation = [
            "V1.17V is the scheduled three-run adversarial review over the new cooling-reacceleration branch.",
            "All three reviewers converged that this branch is stronger than the recently degraded breakout-damage line, because it keeps a positive broader external-pool gap.",
            "They also converged that time-split instability and false-positive overhang still block replay-facing use. The branch stays alive, but only as candidate-only and only for one more non-replay audit cycle.",
        ]
        return V117VCpoStuThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117VCpoStuThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117VCpoStuThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117s_payload=json.loads((repo_root / "reports" / "analysis" / "v117s_cpo_cooling_reacceleration_discovery_v1.json").read_text(encoding="utf-8")),
        v117t_payload=json.loads((repo_root / "reports" / "analysis" / "v117t_cpo_cooling_reacceleration_external_audit_v1.json").read_text(encoding="utf-8")),
        v117u_payload=json.loads((repo_root / "reports" / "analysis" / "v117u_cpo_cooling_reacceleration_time_split_validation_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117v_cpo_stu_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
