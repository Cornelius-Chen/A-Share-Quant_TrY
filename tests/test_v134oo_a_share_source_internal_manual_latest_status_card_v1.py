from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134oo_a_share_source_internal_manual_latest_status_card_v1 import (
    V134OOAShareSourceInternalManualLatestStatusCardV1Analyzer,
)


def test_source_internal_manual_latest_status_card_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OOAShareSourceInternalManualLatestStatusCardV1Analyzer(repo_root).analyze()

    assert result.summary["queue_row_count"] == 4
    assert result.summary["manual_review_completed_count"] == 4
    assert result.summary["primary_completed_count"] == 1
    assert result.summary["independent_completed_count"] == 2
    assert result.summary["sibling_completed_count"] == 1
    assert result.summary["unsatisfied_precondition_count"] == 1


def test_source_internal_manual_latest_status_card_states() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OOAShareSourceInternalManualLatestStatusCardV1Analyzer(repo_root).analyze()

    states = {row["component"]: row["component_state"] for row in result.status_rows}
    assert states["source_internal_manual_lane"] == "manual_review_completed_pending_runtime_promotion"
    assert states["promotion_preconditions"] == "runtime_only_unsatisfied_after_manual_closure"
