from pathlib import Path

from a_share_quant.strategy.v112q_parallel_collection_draft_batch_v1 import (
    V112QParallelCollectionDraftBatchAnalyzer,
    load_json_report,
)


def test_v112q_parallel_collection_draft_batch_is_review_ready() -> None:
    analyzer = V112QParallelCollectionDraftBatchAnalyzer()
    result = analyzer.analyze(
        schema_payload=load_json_report(Path("reports/analysis/v112q_cpo_information_registry_schema_v1.json"))
    )

    assert result.summary["adjacent_official_anchor_count"] >= 10
    assert result.summary["chronology_source_count"] >= 5
    assert result.summary["future_catalyst_calendar_count"] >= 8
    assert result.summary["ready_for_owner_review"] is True
