from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V119ACpoXyzFalsePositiveControlTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V119ACpoXyzFalsePositiveControlTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v118x_payload: dict[str, Any],
        v118y_payload: dict[str, Any],
        v118z_payload: dict[str, Any],
    ) -> V119ACpoXyzFalsePositiveControlTriageReport:
        summary = {
            "acceptance_posture": "freeze_v119a_cpo_xyz_false_positive_control_triage_v1",
            "triage_scope": "V118X_V118Y_V118Z",
            "parent_branch_name": "sustained_participation_non_chase_score_candidate",
            "parent_branch_status": "candidate_only",
            "control_branch_name": "sustained_participation_non_chase_prior_heat_late_fade_control_candidate",
            "control_branch_status": "dead",
            "hard_candidate_allowed": False,
            "candidate_only_allowed": False,
            "soft_expectancy_component_allowed": False,
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "authoritative_current_problem": "same_family_false_positive_control_without_material_external_or_time_split_gain",
            "recommended_next_posture": "drop_same_family_false_positive_control_and_do_not_reopen_without_new_orthogonal_hardening_idea",
        }
        triage_rows = [
            {
                "reviewer": "Pauli",
                "hard_conclusion": "dead",
                "key_reason": "The control line produced no material external or chronology gain and should be killed without killing the parent family.",
            },
            {
                "reviewer": "Tesla",
                "hard_conclusion": "stop_control_keep_family",
                "key_reason": "The control remains same-family carving with unchanged balanced accuracy, so the subline should stop even if the family stays candidate-only.",
            },
            {
                "reviewer": "James",
                "hard_conclusion": "stop_control_keep_family",
                "key_reason": "The branch-level hardening did not improve the weak chronology bucket, so more same-family control work would be tunnel behavior.",
            },
            {
                "reviewer": "Codex",
                "hard_conclusion": "dead_control_keep_parent_candidate_only",
                "key_reason": (
                    f"V118X control_helpful={v118x_payload['summary']['control_helpful']}, "
                    f"V118Y best_bal_acc={v118y_payload['summary']['best_balanced_accuracy']}, "
                    f"V118Z mean_test_bal_acc={v118z_payload['summary']['mean_test_balanced_accuracy']}."
                ),
            },
        ]
        interpretation = [
            "V1.19A freezes the XYZ hardening cycle so the project does not keep spending budget on a same-family false-positive control that changed almost nothing.",
            "The key distinction is explicit: the false-positive control branch is dead, while the parent sustained-participation non-chase family remains candidate-only from V1.18W.",
            "The next cycle must not revisit this prior-heat/late-fade control unless a genuinely orthogonal hardening idea appears.",
        ]
        return V119ACpoXyzFalsePositiveControlTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119ACpoXyzFalsePositiveControlTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119ACpoXyzFalsePositiveControlTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118x_payload=json.loads((repo_root / "reports" / "analysis" / "v118x_cpo_sustained_participation_false_positive_control_discovery_v1.json").read_text(encoding="utf-8")),
        v118y_payload=json.loads((repo_root / "reports" / "analysis" / "v118y_cpo_sustained_participation_false_positive_control_external_audit_v1.json").read_text(encoding="utf-8")),
        v118z_payload=json.loads((repo_root / "reports" / "analysis" / "v118z_cpo_sustained_participation_false_positive_control_time_split_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119a_cpo_xyz_false_positive_control_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
