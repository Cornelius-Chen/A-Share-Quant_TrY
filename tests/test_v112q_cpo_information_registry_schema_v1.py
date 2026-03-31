from pathlib import Path

from a_share_quant.strategy.v112q_cpo_information_registry_schema_v1 import (
    V112QCPOInformationRegistrySchemaAnalyzer,
    load_json_report,
)


def test_v112q_schema_freezes_layers_buckets_and_feature_slots() -> None:
    analyzer = V112QCPOInformationRegistrySchemaAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112q_phase_charter_v1.json")),
        registry_payload=load_json_report(Path("reports/analysis/v112p_cpo_full_cycle_information_registry_v1.json")),
        subagent_policy_payload=load_json_report(Path("reports/analysis/v112h_subagent_exploration_policy_v2.json")),
    )

    assert result.summary["information_layer_count"] == 9
    assert result.summary["bucket_count"] == 5
    assert result.summary["feature_slot_count"] >= 30
    assert result.summary["subagent_collection_task_count"] >= 4
    assert result.summary["recommended_parallel_collection_now"] == 2
