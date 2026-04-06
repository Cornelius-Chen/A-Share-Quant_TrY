from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class V121SCpoPQRThreeRunAdversarialTriageReport:
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


class V121SCpoPQRThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V121SCpoPQRThreeRunAdversarialTriageReport:
        v121p = json.loads((self.repo_root / "reports" / "analysis" / "v121p_cpo_reduce_context_separation_discovery_v1.json").read_text(encoding="utf-8"))
        v121q = json.loads((self.repo_root / "reports" / "analysis" / "v121q_cpo_reduce_context_separation_external_audit_v1.json").read_text(encoding="utf-8"))
        v121r = json.loads((self.repo_root / "reports" / "analysis" / "v121r_cpo_reduce_context_separation_time_split_validation_v1.json").read_text(encoding="utf-8"))

        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "classification": "explanatory_only",
                "replay_facing_allowed": False,
                "hard_reasons": [
                    "External surface is only mildly positive.",
                    "Time-split minimum balanced accuracy collapses too far.",
                    "The line is too sample-thin to remain candidate-only.",
                ],
            },
            {
                "reviewer": "Tesla",
                "classification": "explanatory_only",
                "replay_facing_allowed": False,
                "hard_reasons": [
                    "Chronology is visibly unstable, especially on the 2023 holdout.",
                    "The branch explains some context differences but does not survive candidate-grade review.",
                ],
            },
            {
                "reviewer": "James",
                "classification": "explanatory_only",
                "replay_facing_allowed": False,
                "hard_reasons": [
                    "The branch helps describe reduce context, but it does not support action selection.",
                    "Replay-facing use would be unjustified.",
                ],
            },
        ]

        authoritative_conclusion = {
            "branch_name": "reduce_context_separation_score_candidate",
            "authoritative_status": "explanatory_only",
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "majority_vote": {
                "explanatory_only": 3,
            },
            "why_not_candidate": [
                "external best balanced accuracy 0.662605 is only moderate",
                "time-split mean/min 0.519735 / 0.351852 is too unstable",
                "positive reduce row count is still only 14",
            ],
            "next_posture": "archive_as_reduce_context_explanation_and_stop_candidate_budget",
        }

        summary = {
            "acceptance_posture": "freeze_v121s_cpo_pqr_three_run_adversarial_triage_v1",
            "related_runs": ["V121P", "V121Q", "V121R"],
            "candidate_discriminator_name": "reduce_context_separation_score_candidate",
            "discovery_mean_gap_positive_minus_negative": v121p["summary"]["candidate_score_mean_gap_positive_minus_negative"],
            "external_best_balanced_accuracy": v121q["summary"]["best_balanced_accuracy"],
            "time_split_mean_test_balanced_accuracy": v121r["summary"]["mean_test_balanced_accuracy"],
            "time_split_min_test_balanced_accuracy": v121r["summary"]["min_test_balanced_accuracy"],
            "authoritative_status": "explanatory_only",
            "replay_facing_allowed": False,
        }
        interpretation = [
            "V1.21S freezes the adversarial verdict for the reduce-context separation branch.",
            "The branch adds explanatory value, but chronology failure and sample thinness push it below candidate-only status.",
            "This closes the current reduce-context separation cycle.",
        ]
        return V121SCpoPQRThreeRunAdversarialTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            authoritative_conclusion=authoritative_conclusion,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V121SCpoPQRThreeRunAdversarialTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121SCpoPQRThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121s_cpo_pqr_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
