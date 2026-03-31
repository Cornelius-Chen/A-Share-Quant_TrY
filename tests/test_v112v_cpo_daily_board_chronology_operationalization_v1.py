from pathlib import Path

from a_share_quant.strategy.v112v_cpo_daily_board_chronology_operationalization_v1 import (
    V112VCPODailyBoardChronologyOperationalizationAnalyzer,
    load_json_report,
)


def test_v112v_operationalization_freezes_daily_board_table_spec() -> None:
    analyzer = V112VCPODailyBoardChronologyOperationalizationAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112v_phase_charter_v1.json")),
        schema_payload=load_json_report(Path("reports/analysis/v112q_cpo_information_registry_schema_v1.json")),
        chronology_payload=load_json_report(Path("reports/analysis/v112s_cpo_chronology_normalization_v1.json")),
        draft_batch_payload=load_json_report(Path("reports/analysis/v112q_parallel_collection_draft_batch_v1.json")),
    )
    assert result.summary["daily_series_count"] == 5
    assert result.summary["table_column_count"] == 12
    assert result.summary["remaining_operational_gap_count"] == 3
