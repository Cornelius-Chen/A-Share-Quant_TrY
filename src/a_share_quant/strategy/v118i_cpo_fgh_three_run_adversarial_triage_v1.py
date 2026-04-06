from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class V118ICpoFghThreeRunAdversarialTriageReport:
    summary: dict[str, object]
    triage_rows: list[dict[str, object]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V118ICpoFghThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v118f_payload: dict[str, object],
        v118g_payload: dict[str, object],
        v118h_payload: dict[str, object],
    ) -> V118ICpoFghThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v118i_cpo_fgh_three_run_adversarial_triage_v1",
            "triage_scope": "V118F_V118G_V118H",
            "add_vs_entry_branch_status": "degraded_to_explanatory_only",
            "promotion_allowed": False,
            "replay_facing_expansion_allowed": False,
            "shadow_replay_allowed": False,
            "mainline_investment_allowed": False,
            "candidate_only_allowed": False,
            "explanatory_only_allowed": True,
            "authoritative_current_problem": "role_year_entanglement_not_threshold_tuning",
            "recommended_next_posture": "stop_branch_training_and_keep_as_explanatory_layer_only",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "degrade_after_role_holdout_failure",
                "key_reason": "The branch looks strong on the narrowed strong-entry surface, but role-family holdouts break it badly enough to end mainline investment.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "explanatory_only_due_to_object_shift",
                "key_reason": "The branch has explanatory value because it exposes role-year object shift, but it is not a stable action discriminator.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "stop_training_keep_explanation",
                "key_reason": "Role-year entanglement dominates this branch. Keep it only to explain chronology failure rather than as a live candidate line.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "degrade_to_explanatory_only",
                "key_reason": (
                    f"V118F best_bal_acc={v118f_payload['summary']['best_balanced_accuracy']}, "
                    f"V118G mean_role_holdout_bal_acc={v118g_payload['summary']['mean_evaluable_test_balanced_accuracy']}, "
                    f"V118H interpretation={v118h_payload['summary']['authoritative_interpretation']}."
                ),
            },
        ]
        interpretation = [
            "V1.18I is the scheduled three-run adversarial review over the add-vs-strong-entry branch after strengthening the entry surface and challenging the branch under role holdouts.",
            "All three reviewers converged that the branch should be degraded, not because the add-vs-entry problem was wrong, but because the current solution is mostly tracking role-year pockets rather than a stable action distinction.",
            "The branch therefore stops as a candidate line and remains only as an explanatory layer for chronology and object-shift failure.",
        ]
        return V118ICpoFghThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118ICpoFghThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V118ICpoFghThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118f_payload=json.loads((repo_root / "reports" / "analysis" / "v118f_cpo_add_vs_strong_entry_external_audit_v1.json").read_text(encoding="utf-8")),
        v118g_payload=json.loads((repo_root / "reports" / "analysis" / "v118g_cpo_add_vs_entry_role_family_holdout_v1.json").read_text(encoding="utf-8")),
        v118h_payload=json.loads((repo_root / "reports" / "analysis" / "v118h_cpo_add_vs_entry_role_year_entanglement_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118i_cpo_fgh_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
