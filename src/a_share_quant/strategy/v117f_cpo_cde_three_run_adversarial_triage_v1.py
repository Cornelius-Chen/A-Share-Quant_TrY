from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V117FCpoCdeThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V117FCpoCdeThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v117c_payload: dict[str, Any],
        v117d_payload: dict[str, Any],
        v117e_payload: dict[str, Any],
    ) -> V117FCpoCdeThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v117f_cpo_cde_three_run_adversarial_triage_v1",
            "triage_scope": "V117C_V117D_V117E",
            "continuation_integrity_candidate_status": "degraded_to_explanatory_component_only",
            "promotion_allowed": False,
            "replay_facing_expansion_allowed": False,
            "new_standalone_gate_allowed": False,
            "authoritative_current_problem": "need_new_quality_side_discriminator_not_same_family_continuation_integrity_extension",
            "recommended_next_posture": "stop_mainline_investment_in_continuation_integrity_and_retain_only_as_explanatory_audit_field",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "same_sample_explainer_not_new_constraint",
                "key_reason": "V117D already shows standalone_threshold_usable_now=false and V117E retained internal gap is too weak to justify continued mainline investment.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "weak_increment_not_new_execution_axis",
                "key_reason": "The candidate mostly re-encodes pc1-family quality features and does not create a genuinely new timing or execution discriminator.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "explanatory_gain_without_training_gain",
                "key_reason": "The line can explain why q0.25 is cleaner than hot-only, but it does not reliably refine retained hits into better add decisions.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "degrade_now",
                "key_reason": (
                    f"V117C gap={v117c_payload['summary']['candidate_score_mean_gap_q25_minus_hot_only']}, "
                    f"but V117D best standalone threshold still unusable and V117E retained mean gap only "
                    f"{v117e_payload['summary']['mean_score_gap_positive_minus_weak']}."
                ),
            },
        ]
        interpretation = [
            "V1.17F is the scheduled three-run adversarial review over V117C/V117D/V117E.",
            "All three reviewers converged on the same point: the continuation-integrity score has explanatory value but does not justify further mainline replay-facing investment.",
            "This formally ends the current continuation-integrity branch as a candidate quality law. The score survives only as an explanatory audit component.",
        ]
        return V117FCpoCdeThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117FCpoCdeThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117FCpoCdeThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117c_payload=json.loads((repo_root / "reports" / "analysis" / "v117c_cpo_quality_side_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
        v117d_payload=json.loads((repo_root / "reports" / "analysis" / "v117d_cpo_continuation_integrity_candidate_audit_v1.json").read_text(encoding="utf-8")),
        v117e_payload=json.loads((repo_root / "reports" / "analysis" / "v117e_cpo_continuation_integrity_retained_set_refinement_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117f_cpo_cde_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
