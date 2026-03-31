from __future__ import annotations

from a_share_quant.strategy.v112g_feature_schema_v2 import V112GFeatureSchemaV2Analyzer


def test_v112g_feature_schema_v2_freezes_three_new_features() -> None:
    result = V112GFeatureSchemaV2Analyzer().analyze(
        phase_charter_payload={"summary": {"ready_for_feature_schema_v2_next": True}},
        refinement_design_payload={"catalyst_state_refinement_rows": [{"semantic_question": "fresh"}, {"semantic_question": "persist"}, {"semantic_question": "breadth"}]},
    )

    assert result.summary["new_feature_count"] == 3
    assert result.summary["total_feature_count_v2"] == 15
