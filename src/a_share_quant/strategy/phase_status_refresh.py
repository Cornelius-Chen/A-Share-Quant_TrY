from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PhaseStatusRefreshStep:
    step: int
    name: str
    command: list[str]
    report_path: Path


@dataclass(slots=True)
class PhaseStatusRefreshPlan:
    project_root: Path
    steps: list[PhaseStatusRefreshStep]

    @property
    def final_report_path(self) -> Path:
        return self.steps[-1].report_path


def build_phase_status_refresh_plan(project_root: Path) -> PhaseStatusRefreshPlan:
    reports_dir = project_root / "reports" / "analysis"
    steps = [
        PhaseStatusRefreshStep(
            step=1,
            name="refresh_readiness",
            command=[
                "python",
                "scripts/run_next_batch_refresh_readiness.py",
                "--config",
                "config/next_batch_refresh_readiness_v1.yaml",
            ],
            report_path=reports_dir / "next_batch_refresh_readiness_v1.json",
        ),
        PhaseStatusRefreshStep(
            step=2,
            name="trigger_monitor",
            command=[
                "python",
                "scripts/run_refresh_trigger_monitor.py",
                "--config",
                "config/refresh_trigger_monitor_v1.yaml",
            ],
            report_path=reports_dir / "refresh_trigger_monitor_v1.json",
        ),
        PhaseStatusRefreshStep(
            step=3,
            name="action_plan",
            command=[
                "python",
                "scripts/run_refresh_trigger_action_plan.py",
                "--config",
                "config/refresh_trigger_action_plan_v1.yaml",
            ],
            report_path=reports_dir / "refresh_trigger_action_plan_v1.json",
        ),
        PhaseStatusRefreshStep(
            step=4,
            name="phase_snapshot",
            command=[
                "python",
                "scripts/run_phase_status_snapshot.py",
                "--config",
                "config/phase_status_snapshot_v1.yaml",
            ],
            report_path=reports_dir / "phase_status_snapshot_v1.json",
        ),
    ]
    return PhaseStatusRefreshPlan(project_root=project_root, steps=steps)
