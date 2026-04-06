from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class V118NCpoKlmSoftComponentTriageReport:
    summary: dict[str, object]
    triage_rows: list[dict[str, object]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V118NCpoKlmSoftComponentTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v118k_payload: dict[str, object],
        v118l_payload: dict[str, object],
        v118m_payload: dict[str, object],
    ) -> V118NCpoKlmSoftComponentTriageReport:
        summary = {
            "acceptance_posture": "freeze_v118n_cpo_klm_soft_component_triage_v1",
            "triage_scope": "V118K_V118L_V118M",
            "breakout_damage_soft_component_status": "archived_soft_component",
            "active_integration_allowed": False,
            "candidate_training_allowed": False,
            "replay_facing_allowed": False,
            "authoritative_current_problem": "no_material_integration_gain_over_cooling_baseline",
            "recommended_next_posture": "archive_breakout_damage_soft_component_and_keep_only_for_explanatory_or_future_interaction_use",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "archive_it",
                "key_reason": "The best alpha is still zero, so the soft component adds no real integration value.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "archived_soft_component_not_active",
                "key_reason": "The branch deserves to survive above pure explanation, but only in archive form because active integration produced no material gain.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "stop_active_integration",
                "key_reason": "If the integrated optimum is alpha zero, the component should stay archived and stop consuming active research effort.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "archive_breakout_damage_soft_component",
                "key_reason": (
                    f"V118K best_alpha={v118k_payload['summary']['best_alpha']}, "
                    f"V118L best_bal_acc={v118l_payload['summary']['best_balanced_accuracy']}, "
                    f"V118M stability_posture={v118m_payload['summary']['stability_posture']}."
                ),
            },
        ]
        interpretation = [
            "V1.18N is the scheduled triage over the first active integration attempt for the reclassified breakout-damage soft expectancy component.",
            "All three reviewers converged on the same answer: the component may remain archived because it still has conceptual expectancy value, but it should not stay active because its best integration weight is effectively zero.",
            "This closes the breakout-damage afterlife: archived, not dead, but no longer active in the current CPO training line.",
        ]
        return V118NCpoKlmSoftComponentTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118NCpoKlmSoftComponentTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V118NCpoKlmSoftComponentTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118k_payload=json.loads((repo_root / "reports" / "analysis" / "v118k_cpo_breakout_damage_soft_component_integration_review_v1.json").read_text(encoding="utf-8")),
        v118l_payload=json.loads((repo_root / "reports" / "analysis" / "v118l_cpo_breakout_damage_soft_component_external_audit_v1.json").read_text(encoding="utf-8")),
        v118m_payload=json.loads((repo_root / "reports" / "analysis" / "v118m_cpo_breakout_damage_soft_component_time_split_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118n_cpo_klm_soft_component_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
