from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134kp_a_share_feature_foundation_audit_v1 import (
    V134KPAShareFeatureFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KQAShareKPFeatureDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KQAShareKPFeatureDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KQAShareKPFeatureDirectionTriageV1Report:
        audit = V134KPAShareFeatureFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "feature_component": "feature_registry",
                "direction": "retain_as_central_definition_surface_and_add_new_features_here_not_inside_branch_local_outputs",
            },
            {
                "feature_component": "feature_surface",
                "direction": "use_bootstrap_symbolic_and_statistical_features_as_current_pti_input_candidate_surface",
            },
            {
                "feature_component": "representation_backlog",
                "direction": "delay_representation_materialization_until_pti_and_replay_require_it",
            },
            {
                "feature_component": "next_frontier",
                "direction": "move_into_pti_workstream_using_central_feature_surface_and_label_registry_as_input",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134kq_a_share_kp_feature_direction_triage_v1",
            "feature_registry_count": audit.summary["feature_registry_count"],
            "feature_surface_row_count": audit.summary["feature_surface_row_count"],
            "authoritative_status": "feature_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_pti_population",
        }
        interpretation = [
            "V1.34KQ converts the feature audit into direction.",
            "The next move is PTI: features are now centralized enough that time-slice and state-transition layers can begin consuming them.",
        ]
        return V134KQAShareKPFeatureDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KQAShareKPFeatureDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KQAShareKPFeatureDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kq_a_share_kp_feature_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
