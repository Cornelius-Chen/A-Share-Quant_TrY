from pathlib import Path

from a_share_quant.strategy.v112az_cpo_bounded_training_layer_extension_v1 import (
    V112AZCPOBoundedTrainingLayerExtensionAnalyzer,
    load_json_report,
)


def test_v112az_training_layer_extension_is_narrow() -> None:
    analyzer = V112AZCPOBoundedTrainingLayerExtensionAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112az_phase_charter_v1.json")),
        dataset_assembly_payload=load_json_report(Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")),
        branch_training_layer_review_payload=load_json_report(Path("reports/analysis/v112ay_cpo_guarded_branch_training_layer_review_v1.json")),
    )
    assert result.summary["row_count_after_extension"] == 10
    assert result.summary["guarded_branch_row_count"] == 3
