from __future__ import annotations

from a_share_quant.strategy.phase_status_console import PhaseStatusConsoleFormatter


def test_phase_status_console_formats_idle_wait_state() -> None:
    snapshot_payload = {
        "summary": {
            "current_mode": "explicit_no_trigger_wait",
            "all_gates_aligned": True,
            "should_open_refresh": False,
            "active_trigger_count": 0,
            "recommended_operator_posture": "idle_wait_state",
        }
    }
    action_plan_payload = {
        "summary": {"action_mode": "idle_wait_state"},
        "action_rows": [
            {"step": 1, "action_name": "keep_current_substrates_frozen", "command": None},
            {"step": 2, "action_name": "rerun_refresh_monitor_on_new_signal", "command": "python scripts/run_refresh_trigger_monitor.py --config config/refresh_trigger_monitor_v1.yaml"},
        ],
    }

    view = PhaseStatusConsoleFormatter().build_view(
        snapshot_payload=snapshot_payload,
        action_plan_payload=action_plan_payload,
    )

    assert view.headline == "PHASE STATUS: explicit no-trigger wait"
    assert view.exit_code == 0
    assert any("mode: explicit_no_trigger_wait" in bullet for bullet in view.bullets)
