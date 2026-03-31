from pathlib import Path

from a_share_quant.strategy.v112bs_penalized_target_mapping_refinement_v1 import (
    V112BSPenalizedTargetMappingRefinementAnalyzer,
    load_json_report,
)


def test_v112bs_penalized_mapping_runs() -> None:
    analyzer = V112BSPenalizedTargetMappingRefinementAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bs_phase_charter_v1.json")),
        fusion_pilot_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
        training_layer_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["cluster_count"] == 4
    assert result.penalized_cluster_rows
