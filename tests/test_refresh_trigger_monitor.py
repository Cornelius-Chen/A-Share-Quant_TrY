from __future__ import annotations

from a_share_quant.strategy.refresh_trigger_monitor import (
    RefreshTriggerMonitorAnalyzer,
)


def test_refresh_trigger_monitor_stays_closed_when_all_triggers_false() -> None:
    next_batch_refresh_readiness = {
        "summary": {
            "do_open_market_research_v2_refresh_now": False,
            "recommended_next_phase": "wait_for_new_archetype_gap_signal_before_opening_market_research_v2_refresh",
            "v2_seed_secondary_substrate_status": True,
        }
    }
    v2_seed_continuation = {
        "summary": {
            "do_continue_current_v2_seed_replay": False,
            "v2_seed_contributes_specialist_pockets": True,
        }
    }
    q4_capture_acceptance = {"summary": {"do_continue_q4_capture_replay": False}}
    q3_drawdown_acceptance = {"summary": {"do_continue_q3_drawdown_replay": False}}
    specialist_payload = {"summary": {"top_specialist_by_opportunity_count": "baseline_expansion_branch"}}

    result = RefreshTriggerMonitorAnalyzer().analyze(
        next_batch_refresh_readiness=next_batch_refresh_readiness,
        v2_seed_continuation=v2_seed_continuation,
        q4_capture_acceptance=q4_capture_acceptance,
        q3_drawdown_acceptance=q3_drawdown_acceptance,
        specialist_payload=specialist_payload,
    )

    assert result.summary["active_trigger_count"] == 0
    assert result.summary["should_open_refresh"] is False
    assert result.summary["recommended_posture"] == "maintain_waiting_state_until_new_trigger"
