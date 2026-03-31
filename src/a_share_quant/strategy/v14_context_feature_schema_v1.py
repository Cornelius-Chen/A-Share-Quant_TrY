from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V14ContextFeatureSchemaReport:
    summary: dict[str, Any]
    schema_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "schema_rows": self.schema_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V14ContextFeatureSchemaAnalyzer:
    """Freeze the first bounded schema for report-only context features."""

    def analyze(
        self,
        *,
        context_consumption_protocol_payload: dict[str, Any],
        concept_usage_rules_payload: dict[str, Any],
        catalyst_context_audit_payload: dict[str, Any],
    ) -> V14ContextFeatureSchemaReport:
        protocol_summary = dict(context_consumption_protocol_payload.get("summary", {}))
        usage_rows = list(concept_usage_rules_payload.get("usage_rows", []))
        audit_rows = list(catalyst_context_audit_payload.get("audit_rows", []))

        if not bool(protocol_summary.get("ready_for_bounded_context_feature_schema_next")):
            raise ValueError("V1.4 protocol must explicitly allow the bounded context feature schema next.")

        schema_rows = [
            {
                "feature_name": "single_pulse_support",
                "feature_scope": "lane_outcome_context",
                "value_type": "binary_or_count",
                "primary_source": "catalyst_context_audit_v1",
                "binding_rule": "1 when bounded catalyst context resolves to single_pulse for the matched lane or lane-outcome bucket.",
                "report_only": True,
            },
            {
                "feature_name": "multi_day_reinforcement_support",
                "feature_scope": "lane_outcome_context",
                "value_type": "binary_or_count",
                "primary_source": "catalyst_context_audit_v1",
                "binding_rule": "1 when bounded catalyst context resolves to multi_day_reinforcement for the matched lane or lane-outcome bucket.",
                "report_only": True,
            },
            {
                "feature_name": "policy_followthrough_support",
                "feature_scope": "lane_outcome_context",
                "value_type": "binary_or_count",
                "primary_source": "catalyst_context_audit_v1",
                "binding_rule": "1 when bounded catalyst context resolves to policy_followthrough for the matched lane or lane-outcome bucket.",
                "report_only": True,
            },
            {
                "feature_name": "concept_confirmation_depth",
                "feature_scope": "lane_id",
                "value_type": "ordinal",
                "primary_source": "v13_concept_registry_usage_rules_v1",
                "binding_rule": "2 for bounded_context_primary, 1 for bounded_context_secondary, 0 otherwise.",
                "report_only": True,
            },
            {
                "feature_name": "concept_indirectness_level",
                "feature_scope": "lane_id",
                "value_type": "ordinal",
                "primary_source": "v13_concept_registry_usage_rules_v1",
                "binding_rule": "0 for core_confirmed rows, 1 for market_confirmed_indirect rows, higher values remain undefined in the bounded pilot.",
                "report_only": True,
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v14_context_feature_schema_v1",
            "schema_row_count": len(schema_rows),
            "concept_usage_row_count": len(usage_rows),
            "catalyst_audit_row_count": len(audit_rows),
            "report_only_feature_count": sum(1 for row in schema_rows if bool(row["report_only"])),
            "allow_strategy_integration_now": False,
            "ready_for_bounded_discrimination_check_next": len(schema_rows) > 0,
        }
        interpretation = [
            "V1.4 now has explicit report-only context features instead of only protocol-level intentions.",
            "The schema keeps catalyst and concept context separated but consumable under auditable binding rules.",
            "The next legal step is a bounded discrimination check, not model work or strategy integration.",
        ]
        return V14ContextFeatureSchemaReport(
            summary=summary,
            schema_rows=schema_rows,
            interpretation=interpretation,
        )


def write_v14_context_feature_schema_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V14ContextFeatureSchemaReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
