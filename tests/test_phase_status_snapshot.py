from __future__ import annotations

from a_share_quant.strategy.phase_status_snapshot import (
    PhaseStatusSnapshotAnalyzer,
)


def test_phase_status_snapshot_reads_explicit_no_trigger_wait() -> None:
    v11 = {"summary": {"do_continue_current_specialist_loop": False, "recommended_next_phase": "pause_specialist_refinement_and_prepare_new_suspect_batch"}}
    v2 = {"summary": {"do_continue_current_v2_seed_replay": False, "recommended_next_phase": "hold_market_v2_seed_as_secondary_substrate_and_wait_for_next_batch_refresh"}}
    refresh = {"summary": {"do_open_market_research_v2_refresh_now": False, "recommended_next_phase": "wait_for_new_archetype_gap_signal_before_opening_market_research_v2_refresh"}}
    monitor = {"summary": {"should_open_refresh": False, "active_trigger_count": 0, "recommended_posture": "maintain_waiting_state_until_new_trigger"}}
    action = {"summary": {"action_mode": "idle_wait_state", "recommended_next_phase": "wait_for_new_archetype_gap_signal_before_opening_market_research_v2_refresh"}}

    result = PhaseStatusSnapshotAnalyzer().analyze(
        v11_continuation=v11,
        v2_seed_continuation=v2,
        refresh_readiness=refresh,
        trigger_monitor=monitor,
        action_plan=action,
    )

    assert result.summary["current_mode"] == "explicit_no_trigger_wait"
    assert result.summary["all_gates_aligned"] is True
    assert result.summary["should_open_refresh"] is False
