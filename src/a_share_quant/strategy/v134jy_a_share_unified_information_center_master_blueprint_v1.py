from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JYAShareUnifiedInformationCenterMasterBlueprintV1Report:
    summary: dict[str, Any]
    module_rows: list[dict[str, Any]]
    object_chain_rows: list[dict[str, Any]]
    maturity_rows: list[dict[str, Any]]
    current_gap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "module_rows": self.module_rows,
            "object_chain_rows": self.object_chain_rows,
            "maturity_rows": self.maturity_rows,
            "current_gap_rows": self.current_gap_rows,
            "interpretation": self.interpretation,
        }


class V134JYAShareUnifiedInformationCenterMasterBlueprintV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.reference_dir = repo_root / "data" / "reference"
        self.src_dir = repo_root / "src" / "a_share_quant"
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_unified_information_center_module_status_v1.csv"
        )

    def _reference_names(self) -> set[str]:
        return {path.name for path in self.reference_dir.iterdir()} if self.reference_dir.exists() else set()

    def _src_names(self) -> set[str]:
        return {path.name for path in self.src_dir.iterdir() if path.is_dir()} if self.src_dir.exists() else set()

    @staticmethod
    def _status_score(status: str) -> int:
        scores = {
            "present_partial": 1,
            "present_foundational": 2,
            "present_research_grade": 3,
            "missing": 0,
        }
        return scores[status]

    def analyze(self) -> V134JYAShareUnifiedInformationCenterMasterBlueprintV1Report:
        reference_names = self._reference_names()
        src_names = self._src_names()

        module_rows = [
            {
                "module": "identity_entity",
                "must_have_components": "security_master|entity_master|entity_alias_map|calendar_master",
                "current_repo_status": "present_foundational" if "security_master" in reference_names else "missing",
                "repo_evidence": "data/reference/security_master|data/reference/trading_calendar",
                "future_build_target": "full_a_share_identity_and_alias_resolution",
            },
            {
                "module": "taxonomy_business",
                "must_have_components": "concept_mapping|sector_mapping|business_reference|concept_purity|cross_theme_contamination",
                "current_repo_status": (
                    "present_partial"
                    if {"concept_mapping_daily", "sector_mapping_daily"} <= reference_names
                    else "missing"
                ),
                "repo_evidence": "data/reference/concept_mapping_daily|data/reference/sector_mapping_daily",
                "future_build_target": "business_reference_and_concept_purity_layer",
            },
            {
                "module": "market_data",
                "must_have_components": "daily_bars|intraday_bars|adjustment_factors|daily_basic|limit_halt_state|breadth_state",
                "current_repo_status": (
                    "present_partial"
                    if {"adjustment_factors", "stk_limit", "tushare_daily_basic"} <= reference_names
                    else "missing"
                ),
                "repo_evidence": "data/reference/adjustment_factors|data/reference/stk_limit|data/reference/tushare_daily_basic",
                "future_build_target": "full_point_in_time_market_state_surface",
            },
            {
                "module": "event_catalyst",
                "must_have_components": "source_master|document_registry|claim_registry|event_registry|evidence_span_registry",
                "current_repo_status": "present_partial" if "catalyst_registry" in reference_names else "missing",
                "repo_evidence": "data/reference/catalyst_registry",
                "future_build_target": "document_claim_event_evidence_object_model",
            },
            {
                "module": "attention_heat",
                "must_have_components": "heat_axis|attention_anchor|attention_decoy|burst_registry|heat_proxy_views",
                "current_repo_status": "present_research_grade",
                "repo_evidence": "reports/analysis/v134je...v134jx broader attention route",
                "future_build_target": "broader_attention_evidence_and_heat_axis_service",
            },
            {
                "module": "quality_trust",
                "must_have_components": "source_tier|quality_score|corroboration|contradiction_graph|repost_chain",
                "current_repo_status": "missing",
                "repo_evidence": "none",
                "future_build_target": "source_quality_and_noise_resistance_center",
            },
            {
                "module": "label_supervision",
                "must_have_components": "fact_labels|semantic_labels|state_labels|governance_labels|label_registry",
                "current_repo_status": "present_research_grade",
                "repo_evidence": "reports/analysis multi-line v134* supervision outputs",
                "future_build_target": "centralized_cross_project_label_registry",
            },
            {
                "module": "feature_representation",
                "must_have_components": "symbolic_feature_registry|statistical_feature_registry|representation_feature_registry",
                "current_repo_status": "present_partial" if {"strategy", "trend", "regime"} <= src_names else "missing",
                "repo_evidence": "src/a_share_quant/strategy|src/a_share_quant/regime|src/a_share_quant/trend",
                "future_build_target": "versioned_feature_store_with_purity_between_feature_types",
            },
            {
                "module": "replay_execution_support",
                "must_have_components": "pti_event_state_execution_ledger|shadow_replay_lane|shadow_execution_journal|cost_model_registry",
                "current_repo_status": (
                    "present_partial" if {"execution", "portfolio", "backtest"} <= src_names else "missing"
                ),
                "repo_evidence": "src/a_share_quant/execution|src/a_share_quant/backtest|reports/analysis shadow lane outputs",
                "future_build_target": "isolated_shadow_replay_service",
            },
            {
                "module": "governance_ops",
                "must_have_components": "dataset_registry|schema_registry|feature_registry|heartbeat|freeze_reopen_gate|audit_trail",
                "current_repo_status": "present_partial",
                "repo_evidence": "PROJECT_LIMITATION/07_DECISION_LOG.md|PROJECT_LIMITATION/08_RESEARCH_JOURNAL.md",
                "future_build_target": "formal_registry_and_operational_governance_stack",
            },
        ]

        object_chain_rows = [
            {"stage_order": 1, "object_name": "source_master", "required_fields": "source_id|tier|latency_profile|license_status"},
            {"stage_order": 2, "object_name": "document_registry", "required_fields": "document_id|source_id|public_ts|system_visible_ts|content_hash"},
            {"stage_order": 3, "object_name": "claim_registry", "required_fields": "claim_id|document_id|claim_text|specificity|freshness"},
            {"stage_order": 4, "object_name": "evidence_span_registry", "required_fields": "evidence_span_id|document_id|offset_start|offset_end|subject_entity_ids"},
            {"stage_order": 5, "object_name": "event_registry", "required_fields": "event_id|event_type|event_scope|event_occurred_ts|public_ts|system_visible_ts|confidence_score"},
            {"stage_order": 6, "object_name": "label_registry", "required_fields": "label_id|label_layer|label_name|version|source_event_ids"},
            {"stage_order": 7, "object_name": "feature_registry", "required_fields": "feature_id|feature_group|point_in_time_legal|version|upstream_objects"},
            {"stage_order": 8, "object_name": "time_slice_view", "required_fields": "slice_id|decision_ts|visible_event_ids|visible_features|state_version"},
        ]

        maturity_rows = [
            {
                "maturity_stage": "mvp",
                "must_have": "security_master|calendar_master|raw_storage|event_registry|concept_sector_mapping|catalog",
                "acceptance_gate": "identity_time_data_foundation_exists",
            },
            {
                "maturity_stage": "research_grade",
                "must_have": "source_document_claim_event_evidence|quality_scoring|contradiction_graph|label_registry|feature_registry",
                "acceptance_gate": "research_semantics_are_traceable_and_versioned",
            },
            {
                "maturity_stage": "shadow_grade",
                "must_have": "pti_visibility|state_transition_journal|shadow_replay_lane|shadow_execution_journal|cost_model_registry",
                "acceptance_gate": "point_in_time_shadow_replay_is_isolated_and_reproducible",
            },
            {
                "maturity_stage": "live_like_grade",
                "must_have": "latency_model|freshness_monitoring|activation_rules|promotion_gates|anti_noise_filters",
                "acceptance_gate": "system_can_run_live_like_without_execution_binding",
            },
            {
                "maturity_stage": "execution_grade",
                "must_have": "execution_eligible_evidence_gate|operator_override|risk_kill_switch|rollback_reopen_governance|operational_sla",
                "acceptance_gate": "information_center_can_safely_serve_live_decisioning",
            },
        ]

        current_gap_rows = [
            {
                "priority": 1,
                "gap": "entity_alias_and_name_to_symbol_materialization",
                "why_it_blocks_reuse": "broader symbol pool and external evidence cannot be materialized without stable identity resolution",
            },
            {
                "priority": 2,
                "gap": "document_claim_event_evidence_object_model",
                "why_it_blocks_reuse": "raw event references cannot be rated, contradicted, or reused consistently",
            },
            {
                "priority": 3,
                "gap": "source_quality_contradiction_and_repost_control",
                "why_it_blocks_reuse": "noise and repost cascades can pollute labels and future execution gates",
            },
            {
                "priority": 4,
                "gap": "centralized_label_and_feature_registry",
                "why_it_blocks_reuse": "current supervision assets are rich but distributed rather than registry-backed",
            },
            {
                "priority": 5,
                "gap": "pti_event_state_execution_ledger",
                "why_it_blocks_reuse": "research assets cannot yet be consumed by a lawful shadow or live-like state machine",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(module_rows[0].keys()))
            writer.writeheader()
            writer.writerows(module_rows)

        present_module_count = sum(self._status_score(row["current_repo_status"]) > 0 for row in module_rows)
        research_grade_or_better_count = sum(
            row["current_repo_status"] == "present_research_grade" for row in module_rows
        )
        summary = {
            "acceptance_posture": "build_v134jy_a_share_unified_information_center_master_blueprint_v1",
            "module_count": len(module_rows),
            "object_chain_stage_count": len(object_chain_rows),
            "maturity_stage_count": len(maturity_rows),
            "present_module_count": present_module_count,
            "research_grade_or_better_count": research_grade_or_better_count,
            "current_repo_maturity_floor": "mvp_plus_partial_research_foundation",
            "current_repo_target_next_stage": "research_grade_foundation_completion",
            "module_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_unified_information_center_master_blueprint_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34JY formalizes the full-stack A-share information center as a cross-project blueprint rather than another board-specific research branch.",
            "The current repository already contains meaningful identity, market, event, supervision, and governance fragments, but they have not yet been unified into a point-in-time legal object system.",
            "The blueprint is intentionally staged: first complete research-grade identity, event, quality, and registry layers; only then bind them into shadow replay and later execution-facing services.",
        ]
        return V134JYAShareUnifiedInformationCenterMasterBlueprintV1Report(
            summary=summary,
            module_rows=module_rows,
            object_chain_rows=object_chain_rows,
            maturity_rows=maturity_rows,
            current_gap_rows=current_gap_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JYAShareUnifiedInformationCenterMasterBlueprintV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JYAShareUnifiedInformationCenterMasterBlueprintV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jy_a_share_unified_information_center_master_blueprint_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
