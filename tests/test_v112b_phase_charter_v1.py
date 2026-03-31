from __future__ import annotations

from a_share_quant.strategy.v112b_phase_charter_v1 import V112BPhaseCharterAnalyzer


def test_v112b_phase_charter_opens_after_unified_draft() -> None:
    result = V112BPhaseCharterAnalyzer().analyze(
        v112a_pilot_dataset_draft_payload={"summary": {"dataset_row_count": 3}}
    )

    assert result.summary["do_open_v112b_now"] is True
    assert result.summary["ready_for_dataset_freeze_next"] is True
