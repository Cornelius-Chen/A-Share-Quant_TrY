from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nh_a_share_ng_latest_status_direction_triage_v1 import (
    V134NHAShareNGLatestStatusDirectionTriageV1Analyzer,
)


def test_v134nh_latest_status_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NHAShareNGLatestStatusDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "information_center_in_blocker_closure_mode_not_framework_build_mode"


def test_v134nh_latest_status_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NHAShareNGLatestStatusDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["framework_core"]["direction"].startswith("freeze_current_framework")
    assert rows["index_daily_source_horizon"]["direction"].startswith("freeze_negative_result")
