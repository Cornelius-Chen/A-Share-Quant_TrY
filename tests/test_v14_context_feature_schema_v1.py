from __future__ import annotations

from a_share_quant.strategy.v14_context_feature_schema_v1 import (
    V14ContextFeatureSchemaAnalyzer,
)


def test_v14_context_feature_schema_freezes_report_only_features() -> None:
    result = V14ContextFeatureSchemaAnalyzer().analyze(
        context_consumption_protocol_payload={"summary": {"ready_for_bounded_context_feature_schema_next": True}},
        concept_usage_rules_payload={"usage_rows": [{"lane_id": "a"}]},
        catalyst_context_audit_payload={"audit_rows": [{"lane_outcome_label": "opening_led"}]},
    )

    assert result.summary["acceptance_posture"] == "freeze_v14_context_feature_schema_v1"
    assert result.summary["schema_row_count"] == 5
    assert result.summary["report_only_feature_count"] == 5
    assert result.summary["ready_for_bounded_discrimination_check_next"] is True
