from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V118WCpoTuvThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V118WCpoTuvThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v118t_payload: dict[str, Any],
        v118u_payload: dict[str, Any],
        v118v_payload: dict[str, Any],
    ) -> V118WCpoTuvThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v118w_cpo_tuv_three_run_adversarial_triage_v1",
            "triage_scope": "V118T_V118U_V118V",
            "branch_name": "sustained_participation_non_chase_score_candidate",
            "branch_status": "candidate_only",
            "hard_candidate_allowed": False,
            "candidate_only_allowed": True,
            "soft_expectancy_component_allowed": False,
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "authoritative_current_problem": "time_split_instability_despite_positive_external_pool_signal",
            "recommended_next_posture": "continue_one_more_non_replay_audit_cycle_on_false_positive_control_and_temporal_robustness",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "candidate_only",
                "key_reason": "External audit is good enough to keep alive, but chronology is still too weak for hard-candidate status.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "candidate_only",
                "key_reason": "The branch is directionally right on the broad pool, but not stable enough to justify promotion or replay-facing expansion.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "candidate_only",
                "key_reason": "The line deserves another non-replay audit cycle because the external pool is positive, but min time-split performance at 0.375 blocks anything stronger.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "candidate_only",
                "key_reason": (
                    f"V118T gap={v118t_payload['summary']['candidate_score_mean_gap_positive_minus_negative']}, "
                    f"V118U best_bal_acc={v118u_payload['summary']['best_balanced_accuracy']}, "
                    f"V118V min_test_bal_acc={v118v_payload['summary']['min_test_balanced_accuracy']}."
                ),
            },
        ]
        interpretation = [
            "V1.18W is the scheduled three-run adversarial triage for the sustained-participation non-chase branch.",
            "All three reviewers converged on the same middle answer: this line is alive, but only as candidate-only.",
            "The next budget should go to non-replay hardening of false-positive control and temporal robustness, not replay-facing expansion.",
        ]
        return V118WCpoTuvThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118WCpoTuvThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V118WCpoTuvThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118t_payload=json.loads((repo_root / "reports" / "analysis" / "v118t_cpo_sustained_participation_non_chase_discovery_v1.json").read_text(encoding="utf-8")),
        v118u_payload=json.loads((repo_root / "reports" / "analysis" / "v118u_cpo_sustained_participation_non_chase_external_audit_v1.json").read_text(encoding="utf-8")),
        v118v_payload=json.loads((repo_root / "reports" / "analysis" / "v118v_cpo_sustained_participation_non_chase_time_split_validation_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118w_cpo_tuv_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
