from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class V121OCpoLMNThreeRunAdversarialTriageReport:
    summary: dict
    reviewer_rows: list[dict]
    authoritative_conclusion: dict
    interpretation: list[str]

    def as_dict(self) -> dict:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "authoritative_conclusion": self.authoritative_conclusion,
            "interpretation": self.interpretation,
        }


class V121OCpoLMNThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V121OCpoLMNThreeRunAdversarialTriageReport:
        v121l = json.loads((self.repo_root / "reports" / "analysis" / "v121l_cpo_ijk_three_run_adversarial_triage_v1.json").read_text(encoding="utf-8"))
        v121m = json.loads((self.repo_root / "reports" / "analysis" / "v121m_cpo_reduce_side_symbol_holdout_audit_v1.json").read_text(encoding="utf-8"))
        v121n = json.loads((self.repo_root / "reports" / "analysis" / "v121n_cpo_reduce_side_out_of_set_false_positive_audit_v1.json").read_text(encoding="utf-8"))

        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "classification": "candidate_only",
                "replay_facing_allowed": False,
                "hard_reasons": [
                    "Symbol holdout survives, which keeps the line above soft-component status.",
                    "Out-of-set leakage must still be treated as a blocker for replay-facing use.",
                ],
            },
            {
                "reviewer": "Tesla",
                "classification": "candidate_only",
                "replay_facing_allowed": False,
                "hard_reasons": [
                    "This is still the first live reduce-side branch with nontrivial chronology and symbol survival.",
                    "Leakage across action contexts means it is not yet a clean reduce law.",
                ],
            },
            {
                "reviewer": "James",
                "classification": "soft_component",
                "replay_facing_allowed": False,
                "hard_reasons": [
                    "If leakage stays broad, the branch is closer to a generic risk prior than a discrete action trigger.",
                    "The correct posture is still no replay.",
                ],
            },
        ]

        authoritative_conclusion = {
            "branch_name": "board_risk_off_reduce_score_candidate",
            "authoritative_status": "candidate_only",
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "majority_vote": {
                "candidate_only": 2,
                "soft_component": 1,
            },
            "why_not_hard_candidate": [
                "symbol holdout survives but is not dominant enough to justify promotion",
                "cross-context leakage still prevents execution use",
                "the branch remains broad and needs narrower reduce-only conditioning",
            ],
            "next_posture": "continue_non_replay_reduce_narrowing_and_context_separation",
        }

        summary = {
            "acceptance_posture": "freeze_v121o_cpo_lmn_three_run_adversarial_triage_v1",
            "related_runs": ["V121L", "V121M", "V121N"],
            "candidate_discriminator_name": "board_risk_off_reduce_score_candidate",
            "prior_status": v121l["authoritative_conclusion"]["authoritative_status"],
            "symbol_holdout_posture": v121m["summary"]["symbol_generalization_posture"],
            "reduce_pass_rate": v121n["summary"]["reduce_pass_rate"],
            "add_leakage_rate": v121n["summary"]["add_leakage_rate"],
            "entry_leakage_rate": v121n["summary"]["entry_leakage_rate"],
            "close_leakage_rate": v121n["summary"]["close_leakage_rate"],
            "authoritative_status": "candidate_only",
            "replay_facing_allowed": False,
        }
        interpretation = [
            "V1.21O freezes the second adversarial verdict for the first formal reduce-side branch.",
            "Symbol holdout survival keeps the line alive, but action-context leakage blocks any attempt to use it as an execution rule.",
            "The branch remains candidate-only and should only continue through non-replay narrowing.",
        ]
        return V121OCpoLMNThreeRunAdversarialTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            authoritative_conclusion=authoritative_conclusion,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V121OCpoLMNThreeRunAdversarialTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121OCpoLMNThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121o_cpo_lmn_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
