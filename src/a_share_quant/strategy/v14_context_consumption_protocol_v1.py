from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V14ContextConsumptionProtocolReport:
    summary: dict[str, Any]
    protocol: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "protocol": self.protocol,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V14ContextConsumptionProtocolAnalyzer:
    """Freeze the bounded protocol for consuming catalyst and concept context."""

    def analyze(
        self,
        *,
        v14_phase_charter_payload: dict[str, Any],
        concept_usage_rules_payload: dict[str, Any],
        catalyst_context_audit_payload: dict[str, Any],
    ) -> V14ContextConsumptionProtocolReport:
        charter_summary = dict(v14_phase_charter_payload.get("summary", {}))
        usage_summary = dict(concept_usage_rules_payload.get("summary", {}))
        audit_summary = dict(catalyst_context_audit_payload.get("summary", {}))

        protocol = {
            "consumable_inputs": [
                "v13_concept_registry_usage_rules_v1",
                "catalyst_context_audit_v1",
            ],
            "binding_scope_rules": [
                "context rows must bind by lane_id or lane_outcome_label with auditable point-in-time provenance",
                "core_confirmed concept rows may enter bounded context as primary support",
                "market_confirmed_indirect rows may enter bounded context only as secondary support",
                "no context row may override market confirmation or strategy gating",
            ],
            "report_only_context_features": [
                "single_pulse_support",
                "multi_day_reinforcement_support",
                "policy_followthrough_support",
                "concept_confirmation_depth",
                "concept_indirectness_level",
            ],
            "forbidden_actions": [
                "strategy integration",
                "retained-feature promotion",
                "formal model work",
                "widened replay to create context evidence",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v14_context_consumption_protocol_v1",
            "v14_open": bool(charter_summary.get("do_open_v14_now")),
            "concept_usage_rows_available": usage_summary.get("row_count", 0),
            "catalyst_context_separation_present": bool(audit_summary.get("context_separation_present")),
            "report_only_context_feature_count": len(protocol["report_only_context_features"]),
            "allow_strategy_integration_now": False,
            "ready_for_bounded_context_feature_schema_next": True,
        }
        interpretation = [
            "V1.4 should consume only already-bounded concept and catalyst context, not reopen data collection or replay.",
            "Context rows may add report-only discrimination support, but they cannot override existing market confirmation or strategy gates.",
            "The next legal step is a bounded context-feature schema, not direct integration or training work.",
        ]
        return V14ContextConsumptionProtocolReport(
            summary=summary,
            protocol=protocol,
            interpretation=interpretation,
        )


def write_v14_context_consumption_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V14ContextConsumptionProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
