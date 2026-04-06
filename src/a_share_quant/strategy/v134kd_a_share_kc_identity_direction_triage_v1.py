from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134kc_a_share_identity_foundation_audit_v1 import (
    V134KCAShareIdentityFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KDAShareKCIdentityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KDAShareKCIdentityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KDAShareKCIdentityDirectionTriageV1Report:
        audit = V134KCAShareIdentityFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "identity_component": "security_master",
                "direction": "retain_as_current_source_of_truth_for_symbol_identity_and_begin_taxonomy_binding_from_this_artifact",
            },
            {
                "identity_component": "entity_alias_map",
                "direction": "use_as_initial_name_to_symbol_materialization_surface_and_expand_alias_types_later",
            },
            {
                "identity_component": "identity_source_priority_manifest",
                "direction": "retain_explicit_source_priority_rules_and_do_not_allow_ad_hoc_manual_symbol_resolution_to_bypass_them",
            },
            {
                "identity_component": "next_frontier",
                "direction": "move_directly_into_taxonomy_foundation_using_materialized_identity_as_input",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134kd_a_share_kc_identity_direction_triage_v1",
            "materialized_symbol_count": audit.summary["materialized_symbol_count"],
            "materialized_alias_count": audit.summary["materialized_alias_count"],
            "authoritative_status": "identity_workstream_complete_enough_to_freeze_and_use_as_foundation_for_taxonomy",
        }
        interpretation = [
            "V1.34KD converts the identity audit into operating direction.",
            "The identity workstream is now strong enough to freeze as a foundation layer: future work should consume it rather than continuing to improvise identity mappings branch by branch.",
        ]
        return V134KDAShareKCIdentityDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KDAShareKCIdentityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KDAShareKCIdentityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kd_a_share_kc_identity_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
