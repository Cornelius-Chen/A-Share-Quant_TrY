from pathlib import Path

from a_share_quant.strategy.v112r_adjacent_cohort_validation_v1 import (
    V112RAdjacentCohortValidationAnalyzer,
    load_json_report,
)


def test_v112r_adjacent_validation_produces_split_between_validated_and_pending() -> None:
    analyzer = V112RAdjacentCohortValidationAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112r_phase_charter_v1.json")),
        registry_payload=load_json_report(Path("reports/analysis/v112p_cpo_full_cycle_information_registry_v1.json")),
        draft_batch_payload=load_json_report(Path("reports/analysis/v112q_parallel_collection_draft_batch_v1.json")),
    )
    assert result.summary["reviewed_adjacent_row_count"] == 14
    assert result.summary["validated_review_asset_count"] == 5
    assert result.summary["pending_split_or_role_validation_count"] == 9
