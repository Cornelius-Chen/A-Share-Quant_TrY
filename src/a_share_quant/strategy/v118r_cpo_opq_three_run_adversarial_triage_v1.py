from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V118RCpoOpqThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V118RCpoOpqThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v118o_payload: dict[str, Any],
        v118p_payload: dict[str, Any],
        v118q_payload: dict[str, Any],
    ) -> V118RCpoOpqThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v118r_cpo_opq_three_run_adversarial_triage_v1",
            "triage_scope": "V118O_V118P_V118Q",
            "branch_name": "reclaim_absorption_score_candidate",
            "branch_status": "dead",
            "hard_candidate_allowed": False,
            "soft_expectancy_component_allowed": False,
            "explanatory_only_allowed": False,
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "mainline_resource_allocation_allowed": False,
            "authoritative_current_problem": "external_pool_gap_is_negative_and_time_split_is_unstable",
            "recommended_next_posture": "kill_reclaim_absorption_line_and_reopen_quality_side_discovery_elsewhere",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "dead",
                "key_reason": "Discovery starts with a negative gap and both external and chronology checks fail.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "dead",
                "key_reason": "This is not a weak branch but a reversed branch; the direction is wrong on the external pool.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "dead",
                "key_reason": "No candidate or soft-component budget is justified once the external pool gap is negative and time splits remain sub-0.5.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "dead",
                "key_reason": (
                    f"V118O gap={v118o_payload['summary']['candidate_score_mean_gap_positive_minus_negative']}, "
                    f"V118P external_clear={v118p_payload['summary']['external_pool_signal_clear']}, "
                    f"V118Q mean_test_bal_acc={v118q_payload['summary']['mean_test_balanced_accuracy']}."
                ),
            },
        ]
        interpretation = [
            "V1.18R is the scheduled three-run adversarial triage over the reclaim-absorption branch.",
            "All three reviewers converged without ambiguity: the branch is dead, not merely weak.",
            "The project should spend zero additional budget on reclaim-absorption and reopen discovery on a different quality-side axis.",
        ]
        return V118RCpoOpqThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118RCpoOpqThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V118RCpoOpqThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118o_payload=json.loads((repo_root / "reports" / "analysis" / "v118o_cpo_reclaim_absorption_discovery_v1.json").read_text(encoding="utf-8")),
        v118p_payload=json.loads((repo_root / "reports" / "analysis" / "v118p_cpo_reclaim_absorption_external_audit_v1.json").read_text(encoding="utf-8")),
        v118q_payload=json.loads((repo_root / "reports" / "analysis" / "v118q_cpo_reclaim_absorption_time_split_validation_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118r_cpo_opq_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
