from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class V118ECpoBcdThreeRunAdversarialTriageReport:
    summary: dict[str, object]
    triage_rows: list[dict[str, object]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V118ECpoBcdThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v118b_payload: dict[str, object],
        v118c_payload: dict[str, object],
        v118d_payload: dict[str, object],
    ) -> V118ECpoBcdThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v118e_cpo_bcd_three_run_adversarial_triage_v1",
            "triage_scope": "V118B_V118C_V118D",
            "add_vs_entry_branch_status": "retain_candidate_only_for_one_more_non_replay_adversarial_cycle",
            "promotion_allowed": False,
            "replay_facing_expansion_allowed": False,
            "shadow_replay_allowed": False,
            "mainline_investment_allowed": False,
            "candidate_only_allowed": True,
            "authoritative_current_problem": "chronology_instability_in_add_vs_entry_thresholding",
            "recommended_next_posture": "continue_candidate_only_with_non_replay_adversarial_and_out_of_set_audit",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "one_more_cycle_only_not_mainline",
                "key_reason": "The branch has real external-pool separation, but threshold behavior flips across time splits and blocks any replay-facing work.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "candidate_only_with_chronology_failure",
                "key_reason": "The branch solves the right problem on the full add-vs-entry surface, but chronology turns it into an unstable threshold rather than a reliable discriminator.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "keep_alive_but_not_replay_facing",
                "key_reason": "There is enough signal to keep auditing, but not enough stability to justify replay or shadow replay.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "continue_candidate_only_under_strict_replay_ban",
                "key_reason": (
                    f"V118C best_bal_acc={v118c_payload['summary']['best_balanced_accuracy']}, "
                    f"V118D mean_test_bal_acc={v118d_payload['summary']['mean_test_balanced_accuracy']}, "
                    f"V118D min_test_bal_acc={v118d_payload['summary']['min_test_balanced_accuracy']}."
                ),
            },
        ]
        interpretation = [
            "V1.18E is the scheduled three-run adversarial review over the add-vs-strong-entry branch.",
            "All three reviewers converged that B/C/D found a real problem-specific signal, because the branch separates positive add windows from the full entry surface better than the current cooling-reacceleration control branch separates add from generic non-add contexts.",
            "They also converged that chronology instability is still too strong. The branch stays alive only as candidate-only and only for one more non-replay cycle.",
        ]
        return V118ECpoBcdThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118ECpoBcdThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V118ECpoBcdThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118b_payload=json.loads((repo_root / "reports" / "analysis" / "v118b_cpo_add_vs_entry_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
        v118c_payload=json.loads((repo_root / "reports" / "analysis" / "v118c_cpo_add_vs_entry_external_audit_v1.json").read_text(encoding="utf-8")),
        v118d_payload=json.loads((repo_root / "reports" / "analysis" / "v118d_cpo_add_vs_entry_time_split_validation_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118e_cpo_bcd_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
