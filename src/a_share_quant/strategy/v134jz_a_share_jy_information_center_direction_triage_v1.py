from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134jy_a_share_unified_information_center_master_blueprint_v1 import (
    V134JYAShareUnifiedInformationCenterMasterBlueprintV1Analyzer,
)


@dataclass(slots=True)
class V134JZAShareJYInformationCenterDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JZAShareJYInformationCenterDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JZAShareJYInformationCenterDirectionTriageV1Report:
        audit = V134JYAShareUnifiedInformationCenterMasterBlueprintV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "priority_band": "p0",
                "direction": "build_security_master_entity_alias_map_business_reference_and_concept_purity_first",
                "why_now": "identity and concept purity are the first hard blockers for broader symbol evidence reuse",
            },
            {
                "priority_band": "p1",
                "direction": "build_source_document_claim_event_evidence_object_model",
                "why_now": "future policy/news/fundamental streams cannot be trusted or replayed without object separation",
            },
            {
                "priority_band": "p1",
                "direction": "build_source_quality_corroboration_contradiction_and_repost_controls",
                "why_now": "noise resistance must arrive before broader attention and news ingestion scales up",
            },
            {
                "priority_band": "p2",
                "direction": "promote_existing_supervision_assets_into_central_label_and_feature_registries",
                "why_now": "the repo already has rich labels, but they remain branch-local rather than reusable information-center assets",
            },
            {
                "priority_band": "p3",
                "direction": "build_pti_event_state_execution_ledger_and_bind_shadow_replay_only_after_foundational_layers_exist",
                "why_now": "execution-adjacent work should remain downstream of identity, event, and quality foundations",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jz_a_share_jy_information_center_direction_triage_v1",
            "current_repo_maturity_floor": audit.summary["current_repo_maturity_floor"],
            "module_count": audit.summary["module_count"],
            "priority_row_count": len(triage_rows),
            "authoritative_status": "treat_information_center_as_next_foundational_program_and_build_identity_event_quality_layers_before_shadow_binding",
        }
        interpretation = [
            "V1.34JZ converts the master blueprint into an implementation order.",
            "The most important restraint is sequencing: do not rush into shadow binding or execution-facing plumbing before identity, event objects, and quality controls are stable.",
        ]
        return V134JZAShareJYInformationCenterDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JZAShareJYInformationCenterDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JZAShareJYInformationCenterDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jz_a_share_jy_information_center_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
