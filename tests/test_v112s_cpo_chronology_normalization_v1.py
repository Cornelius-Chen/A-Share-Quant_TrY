from pathlib import Path

from a_share_quant.strategy.v112s_cpo_chronology_normalization_v1 import (
    V112SCPOChronologyNormalizationAnalyzer,
    load_json_report,
)


def test_v112s_chronology_normalization_produces_segments_and_gap_rows() -> None:
    analyzer = V112SCPOChronologyNormalizationAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112s_phase_charter_v1.json")),
        draft_batch_payload=load_json_report(Path("reports/analysis/v112q_parallel_collection_draft_batch_v1.json")),
    )
    assert result.summary["chronology_segment_count"] == 9
    assert result.summary["timing_gap_count"] == 10
    assert result.summary["normalized_calendar_anchor_count"] == 10
