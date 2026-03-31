from pathlib import Path

from a_share_quant.strategy.v112z_bounded_cycle_reconstruction_pass_v1 import (
    V112ZBoundedCycleReconstructionPassAnalyzer,
    load_json_report,
)


def test_v112z_bounded_cycle_reconstruction_pass_preserves_ambiguity() -> None:
    analyzer = V112ZBoundedCycleReconstructionPassAnalyzer()
    result = analyzer.analyze(
        operational_charter_payload=load_json_report(Path("reports/analysis/v112z_operational_charter_v1.json")),
        protocol_payload=load_json_report(Path("reports/analysis/v112z_cycle_reconstruction_protocol_v1.json")),
        registry_schema_payload=load_json_report(Path("reports/analysis/v112q_cpo_information_registry_schema_v1.json")),
        pilot_dataset_payload=load_json_report(Path("reports/analysis/v112b_pilot_dataset_freeze_v1.json")),
        adjacent_validation_payload=load_json_report(Path("reports/analysis/v112r_adjacent_cohort_validation_v1.json")),
        chronology_payload=load_json_report(Path("reports/analysis/v112s_cpo_chronology_normalization_v1.json")),
        daily_board_payload=load_json_report(
            Path("reports/analysis/v112v_cpo_daily_board_chronology_operationalization_v1.json")
        ),
        future_calendar_payload=load_json_report(
            Path("reports/analysis/v112w_cpo_future_catalyst_calendar_operationalization_v1.json")
        ),
        spillover_truth_payload=load_json_report(Path("reports/analysis/v112t_cpo_spillover_truth_check_v1.json")),
        spillover_factor_payload=load_json_report(
            Path("reports/analysis/v112x_cpo_spillover_factor_candidacy_review_v1.json")
        ),
        adjacent_split_payload=load_json_report(
            Path("reports/analysis/v112y_cpo_adjacent_role_split_sidecar_probe_v1.json")
        ),
    )
    assert result.summary["cycle_absorption_review_success"] is True
    assert result.summary["formal_training_still_forbidden"] is True
    assert result.summary["reconstructed_stage_window_count"] >= 8
    assert any(row["ambiguity_family"] == "pending_adjacent_role_split" for row in result.residual_ambiguity_rows)
