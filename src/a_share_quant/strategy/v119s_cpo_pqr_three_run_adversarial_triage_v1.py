from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V119SCpoPqrThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V119SCpoPqrThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v119p_payload: dict[str, Any],
        v119q_payload: dict[str, Any],
        v119r_payload: dict[str, Any],
    ) -> V119SCpoPqrThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v119s_cpo_pqr_three_run_adversarial_triage_v1",
            "triage_scope": "V119P_V119Q_V119R",
            "branch_name": "participation_turnover_elg_support_score_candidate",
            "branch_status": "candidate_only",
            "hard_candidate_allowed": False,
            "candidate_only_allowed": True,
            "soft_expectancy_component_allowed": False,
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "authoritative_current_problem": "object_and_context_shift_failure_blocks_hard_candidate_status",
            "recommended_next_posture": "downgrade_to_candidate_only_and_do_not_expand_family_until_a_new_orthogonal_fix_idea_exists",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "candidate_only",
                "key_reason": "Symbol and role holdouts broke too hard for hard-candidate language, but the line is not fully dead because prior chronology evidence was genuinely strong.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "no_response_timeout",
                "key_reason": "No response before freeze; authoritative decision falls back to the returned reviewer majority plus the measured failure surface.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "candidate_only",
                "key_reason": "The branch must be downgraded from hard candidate because object-shift and context-leakage surfaces are too weak, but it still retains enough prior evidence to survive as candidate-only.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "downgrade_to_candidate_only",
                "key_reason": (
                    f"V119P mean/min symbol_holdout={v119p_payload['summary']['mean_evaluable_test_balanced_accuracy']}/{v119p_payload['summary']['min_evaluable_test_balanced_accuracy']}, "
                    f"V119Q mean/min role_holdout={v119q_payload['summary']['mean_evaluable_test_balanced_accuracy']}/{v119q_payload['summary']['min_evaluable_test_balanced_accuracy']}, "
                    f"V119R entry/close leakage={v119r_payload['summary']['entry_leakage_rate']}/{v119r_payload['summary']['close_leakage_rate']}."
                ),
            },
        ]
        interpretation = [
            "V1.19S is the scheduled three-run adversarial review for the first non-replay hard candidate after symbol holdout, role holdout, and out-of-set leakage audits.",
            "The point of this triage is simple: if object-shift and context-leakage surfaces break, hard-candidate language must be revoked quickly rather than defended.",
            "The authoritative freeze downgrades the branch back to candidate-only because the failure surface is too clear, even though the branch still remains alive as a narrowed candidate family.",
        ]
        return V119SCpoPqrThreeRunAdversarialTriageReport(summary=summary, triage_rows=triage_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V119SCpoPqrThreeRunAdversarialTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119SCpoPqrThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119p_payload=json.loads((repo_root / "reports" / "analysis" / "v119p_cpo_elg_support_symbol_holdout_audit_v1.json").read_text(encoding="utf-8")),
        v119q_payload=json.loads((repo_root / "reports" / "analysis" / "v119q_cpo_elg_support_role_holdout_audit_v1.json").read_text(encoding="utf-8")),
        v119r_payload=json.loads((repo_root / "reports" / "analysis" / "v119r_cpo_elg_support_out_of_set_false_positive_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(reports_dir=repo_root / "reports" / "analysis", report_name="v119s_cpo_pqr_three_run_adversarial_triage_v1", result=result)
    print(output_path)


if __name__ == "__main__":
    main()
