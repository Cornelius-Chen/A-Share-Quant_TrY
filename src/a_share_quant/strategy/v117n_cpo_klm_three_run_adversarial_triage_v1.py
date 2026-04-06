from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V117NCpoKlmThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V117NCpoKlmThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v117k_payload: dict[str, Any],
        v117l_payload: dict[str, Any],
        v117m_payload: dict[str, Any],
    ) -> V117NCpoKlmThreeRunAdversarialTriageReport:
        summary = {
            "acceptance_posture": "freeze_v117n_cpo_klm_three_run_adversarial_triage_v1",
            "triage_scope": "V117K_V117L_V117M",
            "reverse_signal_branch_status": "degraded_to_secondary_explanatory_drawdown_component",
            "human_heuristic_quantization_status": "protocol_only_not_mainline_training_asset",
            "promotion_allowed": False,
            "replay_facing_expansion_allowed": False,
            "authoritative_current_problem": "focus_mainline_resources_on_breakout_damage_branch_not_reverse_or_heuristic_branch",
            "recommended_next_posture": "deprioritize_reverse_and_heuristic_lines_and_keep_them_only_as_secondary_audit_components",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "reverse_branch_collapses_in_real_conditioned_context",
                "key_reason": "The branch looks acceptable in the broad pool but fails once conditioned to the real main-uptrend held-position problem surface.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "reverse_branch_not_new_axis_heuristics_not_mainline_ready",
                "key_reason": "The reverse line is mostly the negative image of positive quality and human heuristics should remain context-conditioned interaction candidates only.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "no_real_training_increment_after_conditioning",
                "key_reason": "Conditioned reverse-signal performance weakens materially and the heuristic quantization layer remains protocol-level rather than a trainable mainline asset.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "degrade_now",
                "key_reason": (
                    f"V117M conditioned balanced_accuracy={v117m_payload['summary']['best_conditioned_balanced_accuracy']} "
                    f"with conditioned_negative_count={v117m_payload['summary']['conditioned_negative_count']} and "
                    f"conditioning_improves_signal={v117m_payload['summary']['conditioning_improves_signal']}."
                ),
            },
        ]
        interpretation = [
            "V1.17N is the scheduled three-run adversarial review over the reverse-signal branch and the human-heuristic quantization protocol.",
            "All three reviewers converged on the same answer: the reverse branch does not survive conditioning into the actual main-uptrend held-position problem, and the human-heuristic layer is still protocol-only.",
            "This formally demotes both lines away from the current CPO mainline. They survive only as low-priority explanatory or interaction-side components.",
        ]
        return V117NCpoKlmThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117NCpoKlmThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117NCpoKlmThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117k_payload=json.loads((repo_root / "reports" / "analysis" / "v117k_cpo_reverse_signal_candidate_discovery_v1.json").read_text(encoding="utf-8")),
        v117l_payload=json.loads((repo_root / "reports" / "analysis" / "v117l_cpo_human_heuristic_signal_quantization_protocol_v1.json").read_text(encoding="utf-8")),
        v117m_payload=json.loads((repo_root / "reports" / "analysis" / "v117m_cpo_reverse_signal_context_conditioning_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117n_cpo_klm_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
