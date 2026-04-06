from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V117JCpoGhiThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V117JCpoGhiThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v117g_payload: dict[str, Any],
        v117h_payload: dict[str, Any],
        v117i_payload: dict[str, Any],
    ) -> V117JCpoGhiThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v117j_cpo_ghi_three_run_adversarial_triage_v1",
            "triage_scope": "V117G_V117H_V117I",
            "breakout_damage_branch_status": "retain_candidate_only_continue_external_audit",
            "promotion_allowed": False,
            "replay_facing_expansion_allowed": False,
            "new_quality_branch_alive": True,
            "authoritative_current_problem": "out_of_set_and_larger_sample_validation_for_breakout_damage_branch",
            "recommended_next_posture": "continue_breakout_damage_branch_candidate_only_and_do_not_promote_before_wider_audit",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "new_branch_alive_but_small_sample_hallucination_risk",
                "key_reason": "Unlike continuation-integrity, the new branch survives retained-set refinement, but 8 retained rows and 1.0 balanced accuracy are too small-sample-perfect to trust as law.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "new_execution_semantic_axis_but_not_yet_scalable",
                "key_reason": "The branch is centered on breakout efficiency and damage containment rather than the old pc1 continuation package, but its current retained-set neatness is still likely fragile.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "real_training_increment_but_candidate_only",
                "key_reason": "This is the first quality-side branch that still separates positives from weak rows inside the retained family, but it remains too small for promotion.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "continue_but_only_candidate_only",
                "key_reason": (
                    f"V117H external gap={v117h_payload['summary']['mean_score_gap_q25_minus_hot_only']}, "
                    f"V117I retained gap={v117i_payload['summary']['mean_score_gap_positive_minus_weak']}, "
                    f"but retained rows={v117i_payload['summary']['retained_row_count']}."
                ),
            },
        ]
        interpretation = [
            "V1.17J is the scheduled three-run adversarial review over the new breakout-damage branch.",
            "All three reviewers converged that this branch is meaningfully stronger than the old continuation-integrity branch, because it keeps discrimination inside the retained family instead of collapsing there.",
            "They also converged on the blocker: the current sample is still too small and too neat. The branch stays alive, but only as a candidate-only line for wider external audit.",
        ]
        return V117JCpoGhiThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117JCpoGhiThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117JCpoGhiThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117g_payload=json.loads((repo_root / "reports" / "analysis" / "v117g_cpo_breakout_damage_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
        v117h_payload=json.loads((repo_root / "reports" / "analysis" / "v117h_cpo_breakout_damage_candidate_audit_v1.json").read_text(encoding="utf-8")),
        v117i_payload=json.loads((repo_root / "reports" / "analysis" / "v117i_cpo_breakout_damage_retained_set_refinement_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117j_cpo_ghi_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
