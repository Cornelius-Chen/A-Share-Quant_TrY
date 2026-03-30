from __future__ import annotations

from a_share_quant.strategy.refresh_trigger_action_plan import (
    RefreshTriggerActionPlanAnalyzer,
)


def test_refresh_trigger_action_plan_stays_idle_when_no_trigger_is_active() -> None:
    monitor_payload = {
        "summary": {
            "active_trigger_count": 0,
            "should_open_refresh": False,
        }
    }
    readiness_payload = {
        "summary": {
            "recommended_next_phase": "wait_for_new_archetype_gap_signal_before_opening_market_research_v2_refresh"
        }
    }

    result = RefreshTriggerActionPlanAnalyzer().analyze(
        monitor_payload=monitor_payload,
        readiness_payload=readiness_payload,
    )

    assert result.summary["action_mode"] == "idle_wait_state"
    assert result.summary["action_count"] == 3
    assert result.action_rows[1]["command"] == "python scripts/run_refresh_trigger_monitor.py --config config/refresh_trigger_monitor_v1.yaml"
