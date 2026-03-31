from pathlib import Path

from a_share_quant.strategy.v112w_cpo_future_catalyst_calendar_operationalization_v1 import (
    V112WFutureCatalystCalendarOperationalizationAnalyzer,
    load_json_report,
)


def test_v112w_operationalization_freezes_recurring_calendar_spec() -> None:
    analyzer = V112WFutureCatalystCalendarOperationalizationAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112w_phase_charter_v1.json")),
        chronology_payload=load_json_report(Path("reports/analysis/v112s_cpo_chronology_normalization_v1.json")),
        draft_batch_payload=load_json_report(Path("reports/analysis/v112q_parallel_collection_draft_batch_v1.json")),
    )
    assert result.summary["recurring_anchor_count"] == 10
    assert result.summary["table_column_count"] == 12
    assert result.summary["remaining_operational_gap_count"] == 3
