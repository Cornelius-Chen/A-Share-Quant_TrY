from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135at_a_share_as_internal_hot_news_focus_governance_tension_change_direction_triage_v1 import (
    V135ATAShareASInternalHotNewsFocusGovernanceTensionChangeDirectionTriageV1Analyzer,
)


def test_v135at_focus_governance_tension_change_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ATAShareASInternalHotNewsFocusGovernanceTensionChangeDirectionTriageV1Analyzer(
        repo_root
    ).analyze()

    assert report.summary["signal_priority"] in {"p1", "p2"}
    assert report.summary["tension_state_change"] in {"no_previous_baseline", "state_changed", "stable"}


def test_v135at_focus_governance_tension_change_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ATAShareASInternalHotNewsFocusGovernanceTensionChangeDirectionTriageV1Analyzer(
        repo_root
    ).analyze()

    assert len(report.triage_rows) == 3
