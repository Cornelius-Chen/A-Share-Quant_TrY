from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ki_a_share_quality_foundation_audit_v1 import (
    V134KIAShareQualityFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KJAShareKIQualityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KJAShareKIQualityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KJAShareKIQualityDirectionTriageV1Report:
        audit = V134KIAShareQualityFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "quality_component": "source_quality_registry",
                "direction": "retain_bootstrap_source_tiers_and_replace_heuristics_with_reviewed_source_master_enrichment_later",
            },
            {
                "quality_component": "event_quality_registry",
                "direction": "use_bootstrap_evidence_gate_for_shadow_and_research_sorting_only_not_execution",
            },
            {
                "quality_component": "repost_control_registry",
                "direction": "retain_as_first_noise_control_surface_and_expand_from_duplicate_registry_reference_to_real_document_hashing_later",
            },
            {
                "quality_component": "contradiction_backlog",
                "direction": "feed_into_review_jobs_before_attention_and_decision_layers_start_trusting_quality_labels_too_much",
            },
            {
                "quality_component": "next_frontier",
                "direction": "move_into_attention_layer_using_quality_registry_as_guardrail_input",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134kj_a_share_ki_quality_direction_triage_v1",
            "materialized_source_quality_count": audit.summary["materialized_source_quality_count"],
            "materialized_event_quality_count": audit.summary["materialized_event_quality_count"],
            "authoritative_status": "quality_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_attention_with_quality_guardrails",
        }
        interpretation = [
            "V1.34KJ converts the quality audit into direction.",
            "The next move is not to overtrust the heuristics; it is to use them as guardrails while the attention layer and later review jobs start consuming the explicit quality surface.",
        ]
        return V134KJAShareKIQualityDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KJAShareKIQualityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KJAShareKIQualityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kj_a_share_ki_quality_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
