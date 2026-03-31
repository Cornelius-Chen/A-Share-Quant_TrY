from pathlib import Path

from a_share_quant.strategy.v112ba_cpo_10_row_layer_replacement_review_v1 import (
    V112BACPO10RowLayerReplacementReviewAnalyzer,
    load_json_report,
)


def test_v112ba_replaces_7_row_baseline() -> None:
    analyzer = V112BACPO10RowLayerReplacementReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ba_phase_charter_v1.json")),
        training_readiness_payload=load_json_report(Path("reports/analysis/v112al_cpo_bounded_training_readiness_review_v1.json")),
        guarded_branch_pilot_payload=load_json_report(Path("reports/analysis/v112ax_cpo_guarded_branch_admitted_pilot_v1.json")),
        training_layer_extension_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
    )
    assert result.summary["replace_7_row_baseline_now"] is True
