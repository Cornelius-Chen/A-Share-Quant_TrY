from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V119GCpoDefThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V119GCpoDefThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v119d_payload: dict[str, Any],
        v119e_payload: dict[str, Any],
        v119f_payload: dict[str, Any],
    ) -> V119GCpoDefThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v119g_cpo_def_three_run_adversarial_triage_v1",
            "triage_scope": "V119D_V119E_V119F",
            "branch_name": "tushare_turnover_discipline_score_candidate",
            "branch_status": "candidate_only",
            "hard_candidate_allowed": False,
            "candidate_only_allowed": True,
            "soft_expectancy_component_allowed": False,
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "authoritative_current_problem": "single_year_recall_hole_despite_strong_external_and_mean_time_split",
            "recommended_next_posture": "continue_one_more_non_replay_audit_cycle_on_holdout_2024_failure_surface",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "candidate_only",
                "key_reason": "This is stronger than prior quality-side lines, but the 2024 holdout still has zero positive recall and blocks hard-candidate promotion.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "candidate_only",
                "key_reason": "The branch is the strongest new orthogonal hardening line so far, but replay-facing use is still premature while one holdout year remains structurally weak.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "hard_candidate_but_non_replay_only",
                "key_reason": "The external and time-split surface is strong enough to treat the branch as a hard candidate in principle, but not yet replay-facing because the 2024 split still fails.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "candidate_only_consensus_floor",
                "key_reason": (
                    f"V119D gap={v119d_payload['summary']['candidate_score_mean_gap_positive_minus_negative']}, "
                    f"V119E best_bal_acc={v119e_payload['summary']['best_balanced_accuracy']}, "
                    f"V119F mean/min_test_bal_acc={v119f_payload['summary']['mean_test_balanced_accuracy']}/{v119f_payload['summary']['min_test_balanced_accuracy']}."
                ),
            },
        ]
        interpretation = [
            "V1.19G is the scheduled three-run adversarial review for the first Tushare-backed orthogonal hardening branch.",
            "All reviewers agree this line is materially stronger than the prior quality-side branches; the only live disagreement is whether it already deserves hard-candidate language.",
            "The authoritative decision stays conservative: keep it candidate-only, block replay, and spend one more cycle on the 2024 holdout failure surface instead of promoting early.",
        ]
        return V119GCpoDefThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119GCpoDefThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119GCpoDefThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119d_payload=json.loads((repo_root / "reports" / "analysis" / "v119d_cpo_tushare_turnover_discipline_discovery_v1.json").read_text(encoding="utf-8")),
        v119e_payload=json.loads((repo_root / "reports" / "analysis" / "v119e_cpo_tushare_turnover_discipline_external_audit_v1.json").read_text(encoding="utf-8")),
        v119f_payload=json.loads((repo_root / "reports" / "analysis" / "v119f_cpo_tushare_turnover_discipline_time_split_validation_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119g_cpo_def_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
