from pathlib import Path

from a_share_quant.strategy.v112y_cpo_adjacent_role_split_sidecar_probe_v1 import (
    V112YAdjacentRoleSplitSidecarProbeAnalyzer,
    load_json_report,
)


def test_v112y_probe_splits_pending_adjacent_bucket() -> None:
    analyzer = V112YAdjacentRoleSplitSidecarProbeAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112y_phase_charter_v1.json")),
        adjacent_validation_payload=load_json_report(Path("reports/analysis/v112r_adjacent_cohort_validation_v1.json")),
    )
    assert result.summary["reviewed_pending_adjacent_row_count"] == 9
    assert result.summary["split_ready_review_asset_count"] == 6
    assert result.summary["still_pending_row_count"] == 3
