from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from a_share_quant.strategy.phase_status_console import PhaseStatusConsoleFormatter
from a_share_quant.strategy.phase_status_refresh import build_phase_status_refresh_plan


@dataclass(slots=True)
class PhaseGuardResult:
    headline: str
    bullets: list[str]
    exit_code: int


def run_phase_guard(project_root: Path) -> PhaseGuardResult:
    plan = build_phase_status_refresh_plan(project_root)
    for step in plan.steps:
        subprocess.run(step.command, cwd=project_root, check=True)

    reports_dir = project_root / "reports" / "analysis"
    snapshot_path = reports_dir / "phase_status_snapshot_v1.json"
    action_plan_path = reports_dir / "refresh_trigger_action_plan_v1.json"

    with snapshot_path.open("r", encoding="utf-8") as handle:
        snapshot_payload = json.load(handle)
    with action_plan_path.open("r", encoding="utf-8") as handle:
        action_plan_payload = json.load(handle)

    view = PhaseStatusConsoleFormatter().build_view(
        snapshot_payload=snapshot_payload,
        action_plan_payload=action_plan_payload,
    )
    return PhaseGuardResult(
        headline=view.headline,
        bullets=view.bullets,
        exit_code=view.exit_code,
    )
