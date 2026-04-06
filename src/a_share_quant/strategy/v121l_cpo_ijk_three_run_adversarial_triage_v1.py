from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V121LCpoIJKThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    authoritative_conclusion: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "authoritative_conclusion": self.authoritative_conclusion,
            "interpretation": self.interpretation,
        }


class V121LCpoIJKThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V121LCpoIJKThreeRunAdversarialTriageReport:
        v121i = json.loads(
            (self.repo_root / "reports" / "analysis" / "v121i_cpo_reduce_side_board_risk_off_discovery_v1.json").read_text(
                encoding="utf-8"
            )
        )
        v121j = json.loads(
            (self.repo_root / "reports" / "analysis" / "v121j_cpo_reduce_side_board_risk_off_external_audit_v1.json").read_text(
                encoding="utf-8"
            )
        )
        v121k = json.loads(
            (self.repo_root / "reports" / "analysis" / "v121k_cpo_reduce_side_board_risk_off_time_split_validation_v1.json").read_text(
                encoding="utf-8"
            )
        )

        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "classification": "soft_component",
                "replay_facing_allowed": False,
                "hard_reasons": [
                    "External signal is positive but not hard enough for an independent reduce law.",
                    "Time-split stability stays alive but is far from hard-candidate territory.",
                    "The line looks like a broad risk-off prior, not a clean reduce trigger.",
                ],
            },
            {
                "reviewer": "Tesla",
                "classification": "candidate_only",
                "replay_facing_allowed": False,
                "hard_reasons": [
                    "External audit is clearly positive and keeps the branch alive.",
                    "Chronology survives with mean/min balanced accuracy above the stopline.",
                    "Positive sample count remains too thin for hard-candidate status.",
                ],
            },
            {
                "reviewer": "James",
                "classification": "candidate_only",
                "replay_facing_allowed": False,
                "hard_reasons": [
                    "The branch is the first live reduce-side line beyond pure explanation.",
                    "The evidence supports continued non-replay auditing, not replay expansion.",
                    "The branch is still broad and needs narrower reduce-side discipline before any promotion.",
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
                "external best balanced accuracy 0.687336 is positive but not strong enough for promotion",
                "time-split mean/min 0.615348 / 0.525 shows survival, not maturity",
                "positive reduce row count is still only 14",
            ],
            "next_posture": "continue_non_replay_reduce_side_narrowing_before_any_execution_use",
        }

        summary = {
            "acceptance_posture": "freeze_v121l_cpo_ijk_three_run_adversarial_triage_v1",
            "related_runs": ["V121I", "V121J", "V121K"],
            "candidate_discriminator_name": "board_risk_off_reduce_score_candidate",
            "discovery_mean_gap_positive_minus_negative": v121i["summary"]["candidate_score_mean_gap_positive_minus_negative"],
            "external_best_balanced_accuracy": v121j["summary"]["best_balanced_accuracy"],
            "time_split_mean_test_balanced_accuracy": v121k["summary"]["mean_test_balanced_accuracy"],
            "time_split_min_test_balanced_accuracy": v121k["summary"]["min_test_balanced_accuracy"],
            "authoritative_status": "candidate_only",
            "replay_facing_allowed": False,
        }

        interpretation = [
            "V1.21L freezes the first adversarial verdict for the formal reduce-side board risk-off branch.",
            "The branch is alive and stronger than the earlier close-only downside line, but it still lacks the evidence needed for replay-facing use.",
            "The correct next move is continued non-replay narrowing, not execution promotion.",
        ]
        return V121LCpoIJKThreeRunAdversarialTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            authoritative_conclusion=authoritative_conclusion,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121LCpoIJKThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121LCpoIJKThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121l_cpo_ijk_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
