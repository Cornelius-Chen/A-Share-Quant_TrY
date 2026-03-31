from __future__ import annotations

from a_share_quant.strategy.v112a_pilot_object_pool_v1 import V112APilotObjectPoolAnalyzer


def test_v112a_pilot_object_pool_contains_three_reviewable_objects() -> None:
    result = V112APilotObjectPoolAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112a_now": True}},
    )

    assert result.summary["pilot_object_count"] == 3
    assert result.summary["ready_for_label_review_sheet_next"] is True
