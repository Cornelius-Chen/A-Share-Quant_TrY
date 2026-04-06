from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class V117ZCpoWxyThreeRunAdversarialTriageReport:
    summary: dict[str, object]
    triage_rows: list[dict[str, object]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V117ZCpoWxyThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v117w_payload: dict[str, object],
        v117x_payload: dict[str, object],
        v117y_payload: dict[str, object],
    ) -> V117ZCpoWxyThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v117z_cpo_wxy_three_run_adversarial_triage_v1",
            "triage_scope": "V117W_V117X_V117Y",
            "cooling_reacceleration_branch_status": "retain_candidate_only_continue_without_shadow_replay",
            "promotion_allowed": False,
            "replay_facing_expansion_allowed": False,
            "shadow_replay_allowed": False,
            "mainline_investment_allowed": False,
            "candidate_only_allowed": True,
            "authoritative_current_problem": "small_sample_threshold_stability_and_false_positive_rejection_strength",
            "recommended_next_posture": "continue_candidate_only_with_non_replay_out_of_set_false_positive_control_audit",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "real_improvement_but_boundary_not_hard_enough",
                "key_reason": "This is the first version that improves both external-pool separation and time-split stability, but small-sample threshold stability and weak negative rejection still block replay-facing use.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "candidate_only_continue_not_shadow_replay_ready",
                "key_reason": "The branch is materially cleaner than pre-control cooling-reacceleration, yet it still admits too many negatives and should stay candidate-only until false positives are thinner.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "worth_continuing_but_only_inside_non_replay_triage",
                "key_reason": "The control layer has training value and survives time split much better, but the add-pool is still too small to justify replay-facing work.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "retain_candidate_only_and_keep_replay_ban",
                "key_reason": (
                    f"V117X best_bal_acc={v117x_payload['summary']['best_balanced_accuracy']}, "
                    f"V117Y mean_test_bal_acc={v117y_payload['summary']['mean_test_balanced_accuracy']}, "
                    f"V117Y min_test_bal_acc={v117y_payload['summary']['min_test_balanced_accuracy']}."
                ),
            },
        ]
        interpretation = [
            "V1.17Z is the scheduled three-run adversarial review over the false-positive-control refinement of the cooling-reacceleration branch.",
            "All three reviewers converged that W/X/Y materially improved the branch relative to the pre-control candidate, because external-pool discrimination rose and crude time-split stability no longer collapsed.",
            "They also converged that the branch still does not deserve any replay-facing or shadow-replay expansion. The remaining issue is no longer directionality, but boundary hardness: sample count is still small and negative rejection is not yet strong enough.",
        ]
        return V117ZCpoWxyThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117ZCpoWxyThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117ZCpoWxyThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117w_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v117w_cpo_cooling_reacceleration_false_positive_control_discovery_v1.json").read_text(
                encoding="utf-8"
            )
        ),
        v117x_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v117x_cpo_cooling_reacceleration_false_positive_control_external_audit_v1.json").read_text(
                encoding="utf-8"
            )
        ),
        v117y_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v117y_cpo_cooling_reacceleration_false_positive_control_time_split_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117z_cpo_wxy_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
