from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.phase_status_refresh import build_phase_status_refresh_plan


def test_phase_guard_uses_phase_refresh_plan_order() -> None:
    plan = build_phase_status_refresh_plan(Path("D:/Creativity/A-Share-Quant_TrY"))
    assert len(plan.steps) == 4
    assert plan.steps[0].name == "refresh_readiness"
    assert plan.steps[-1].name == "phase_snapshot"
