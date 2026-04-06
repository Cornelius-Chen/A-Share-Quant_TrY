from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class V117RCpoOpqThreeRunAdversarialTriageReport:
    summary: dict[str, object]
    triage_rows: list[dict[str, object]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V117RCpoOpqThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v117o_payload: dict[str, object],
        v117p_payload: dict[str, object],
        v117q_payload: dict[str, object],
    ) -> V117RCpoOpqThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v117r_cpo_opq_three_run_adversarial_triage_v1",
            "triage_scope": "V117O_V117P_V117Q",
            "breakout_damage_branch_status": "degraded_to_candidate_explanatory_component_only",
            "promotion_allowed": False,
            "replay_facing_expansion_allowed": False,
            "mainline_investment_allowed": False,
            "secondary_explanatory_layer_retained": True,
            "authoritative_current_problem": "the_branch_fails_broader_external_and_time_split_validation_even_if_false_positives_are_explainable",
            "recommended_next_posture": "stop_mainline_investment_in_breakout_damage_and_reopen_new_quality_side_discovery_only_after_reset",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "stop_mainline_investment_now",
                "key_reason": "External-pool signal is no longer clear and time-split validation is already weak enough to stop further mainline effort.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "false_positive_overhang_is_the_real_failure_mode",
                "key_reason": "The branch can still tell a good story on neat rows, but the broader pool produces too many false positives and the timing split does not rescue it.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "candidate_only_even_as_training_asset",
                "key_reason": "There is still some learnability, but it is not strong enough to justify replay-facing status or continued mainline training investment.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "degrade_breakout_damage_and_keep_reverse_human_layers_explanatory_only",
                "key_reason": (
                    f"V117O external_clear={v117o_payload['summary']['external_pool_signal_clear']}, "
                    f"V117P mean_test_bal_acc={v117p_payload['summary']['mean_test_balanced_accuracy']}, "
                    f"V117Q top_explanatory_metric={v117q_payload['summary']['top_explanatory_metric']}."
                ),
            },
        ]
        interpretation = [
            "V1.17R is the scheduled adversarial review over the O/P/Q cycle: broader external audit, time-split external validation, and false-positive explanatory audit.",
            "All three reviewers converged that breakout-damage is no longer strong enough to remain the active replay-facing candidate branch once tested on the broader and dirtier surface.",
            "The branch is therefore degraded to candidate/explanatory-only. Reverse-signal and human-heuristic layers remain useful only for false-positive explanation, not as new mainline policy.",
        ]
        return V117RCpoOpqThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117RCpoOpqThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117RCpoOpqThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117o_payload=json.loads((repo_root / "reports" / "analysis" / "v117o_cpo_breakout_damage_external_pool_audit_v1.json").read_text(encoding="utf-8")),
        v117p_payload=json.loads((repo_root / "reports" / "analysis" / "v117p_cpo_breakout_damage_time_split_external_validation_v1.json").read_text(encoding="utf-8")),
        v117q_payload=json.loads((repo_root / "reports" / "analysis" / "v117q_cpo_breakout_damage_false_positive_explanatory_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117r_cpo_opq_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
