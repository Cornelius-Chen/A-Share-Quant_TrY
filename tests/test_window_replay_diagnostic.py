from __future__ import annotations

from datetime import date

from a_share_quant.strategy.window_replay_diagnostic import (
    ReplayTargetWindow,
    WindowReplayDiagnostic,
)


def test_classify_window_behavior_no_entry() -> None:
    diagnostic = WindowReplayDiagnostic()
    window = ReplayTargetWindow(
        window_id="demo_1",
        symbol="000001",
        start_date=date(2024, 1, 10),
        end_date=date(2024, 1, 12),
    )
    classification = diagnostic._classify_window_behavior(
        window=window,
        active_interval=None,
        daily_records=[
            {
                "emitted_actions": [],
                "triggered_entries": [],
            }
        ],
    )
    assert classification == "no_entry"


def test_classify_pair_issue_late_entry_and_early_exit() -> None:
    diagnostic = WindowReplayDiagnostic()
    issue = diagnostic._classify_pair_issue(
        incumbent={
            "classification": "held_through_window",
            "active_interval": {
                "entry_date": "2024-09-17",
                "exit_date": "2024-10-01",
            },
        },
        challenger={
            "classification": "late_entry_and_early_exit",
            "active_interval": {
                "entry_date": "2024-09-20",
                "exit_date": "2024-09-25",
            },
        },
    )
    assert issue == "challenger_late_entry_and_early_exit"
