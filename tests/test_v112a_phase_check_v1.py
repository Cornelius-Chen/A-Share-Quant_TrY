from __future__ import annotations

from a_share_quant.strategy.v112a_phase_check_v1 import V112APhaseCheckAnalyzer


def test_v112a_phase_check_marks_sheet_ready_for_owner_correction() -> None:
    result = V112APhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112a_now": True}},
        pilot_object_pool_payload={"summary": {"pilot_object_count": 3, "repo_seen_object_count": 1, "owner_seeded_object_count": 2}},
        label_review_sheet_payload={"summary": {"review_row_count": 3, "owner_review_required_count": 3}},
    )

    assert result.summary["ready_for_owner_correction_next"] is True
    assert result.summary["allow_training_now"] is False
