from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134kn_a_share_label_foundation_audit_v1 import (
    V134KNAShareLabelFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KOAShareKNLabelDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KOAShareKNLabelDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KOAShareKNLabelDirectionTriageV1Report:
        audit = V134KNAShareLabelFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "label_component": "label_registry",
                "direction": "retain_as_central_definition_surface_and_keep_new_labels_from_being_defined_inside_branch_specific_reports",
            },
            {
                "label_component": "label_assignment_surface",
                "direction": "use_for_fact_and_semantic_bootstrap_only_and_delay_state_and_governance_assignments_until_pti_exists",
            },
            {
                "label_component": "state_label_backlog",
                "direction": "feed_into_pti_workstream_for_future_stateful_assignment",
            },
            {
                "label_component": "governance_label_backlog",
                "direction": "feed_into_serving_and_replay_workstreams_for future action-surface binding",
            },
            {
                "label_component": "next_frontier",
                "direction": "move_into_feature_registry_population_using_central_label_registry_as_input",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134ko_a_share_kn_label_direction_triage_v1",
            "label_definition_count": audit.summary["label_definition_count"],
            "label_assignment_count": audit.summary["label_assignment_count"],
            "authoritative_status": "label_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_feature_registry_population",
        }
        interpretation = [
            "V1.34KO converts the label audit into direction.",
            "Labels are now centralized enough that future work should reuse the registry instead of continuing to mint ad hoc branch-local semantics.",
        ]
        return V134KOAShareKNLabelDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KOAShareKNLabelDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KOAShareKNLabelDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ko_a_share_kn_label_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
