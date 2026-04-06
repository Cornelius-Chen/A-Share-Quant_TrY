from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134kg_a_share_event_foundation_audit_v1 import (
    V134KGAShareEventFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KHAShareKGEventDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KHAShareKGEventDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KHAShareKGEventDirectionTriageV1Report:
        audit = V134KGAShareEventFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "event_component": "source_master",
                "direction": "retain_as_current_bootstrap_source_surface_and_extend_with_source_tier_quality_fields_next",
            },
            {
                "event_component": "document_claim_event_chain",
                "direction": "retain_as_bootstrap_object_chain_and_expand_pti_quality_fields_before_heavy_attention_ingestion",
            },
            {
                "event_component": "evidence_span_registry",
                "direction": "keep_registry_notes_as_bootstrap_evidence_only_and_expand_to_real_span_level_sources_later",
            },
            {
                "event_component": "next_frontier",
                "direction": "move_into_quality_layer_and_point_in_time_enrichment_using_bootstrapped_event_chain_as_input",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134kh_a_share_kg_event_direction_triage_v1",
            "materialized_event_count": audit.summary["materialized_event_count"],
            "authoritative_status": "event_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_quality_and_pti_enrichment",
        }
        interpretation = [
            "V1.34KH converts the event bootstrap into operating direction.",
            "The chain is now real enough to use, but the correct next step is enrichment: quality and PTI expansion, not pretending the bootstrap already equals full document understanding.",
        ]
        return V134KHAShareKGEventDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KHAShareKGEventDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KHAShareKGEventDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kh_a_share_kg_event_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
