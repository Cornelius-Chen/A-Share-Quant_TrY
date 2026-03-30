from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.phase_status_refresh import build_phase_status_refresh_plan


def test_phase_status_refresh_plan_has_expected_order() -> None:
    plan = build_phase_status_refresh_plan(Path("D:/Creativity/A-Share-Quant_TrY"))

    assert [step.name for step in plan.steps] == [
        "refresh_readiness",
        "trigger_monitor",
        "action_plan",
        "phase_snapshot",
    ]
    assert plan.final_report_path.name == "phase_status_snapshot_v1.json"
    assert plan.steps[0].command[1] == "scripts/run_next_batch_refresh_readiness.py"
