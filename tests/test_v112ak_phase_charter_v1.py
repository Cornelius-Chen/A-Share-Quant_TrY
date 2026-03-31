from pathlib import Path

from a_share_quant.strategy.v112ak_phase_charter_v1 import (
    V112AKPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ak_phase_charter_opens_feature_binding_review() -> None:
    analyzer = V112AKPhaseCharterAnalyzer()
    result = analyzer.analyze(
        dataset_assembly_payload=load_json_report(Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")),
    )
    assert result.summary["do_open_v112ak_now"] is True
