from pathlib import Path

from a_share_quant.strategy.v112aa_cpo_bounded_cohort_map_v1 import (
    V112AACPOBoundedCohortMapAnalyzer,
    load_json_report,
)


def test_v112aa_cohort_map_keeps_pending_and_spillover_visible() -> None:
    analyzer = V112AACPOBoundedCohortMapAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112aa_phase_charter_v1.json")),
        reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
        adjacent_validation_payload=load_json_report(Path("reports/analysis/v112r_adjacent_cohort_validation_v1.json")),
        adjacent_split_payload=load_json_report(Path("reports/analysis/v112y_cpo_adjacent_role_split_sidecar_probe_v1.json")),
        spillover_factor_payload=load_json_report(Path("reports/analysis/v112x_cpo_spillover_factor_candidacy_review_v1.json")),
    )
    assert result.summary["object_row_count"] == 20
    assert result.summary["pending_ambiguous_count"] == 3
    assert any(row["cohort_layer"] == "spillover_candidate" for row in result.object_role_time_rows)
