from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pb_a_share_pa_tushare_index_daily_extension_direction_triage_v1 import (
    V134PBASharePATushareIndexDailyExtensionDirectionTriageV1Analyzer,
)


def test_v134pb_tushare_index_daily_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134PBASharePATushareIndexDailyExtensionDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["coverage_end"] >= "2026-03-28"


def test_v134pb_tushare_index_daily_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134PBASharePATushareIndexDailyExtensionDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in result.triage_rows}
    assert directions["replay_reaudit"] == "rerun_index_daily_gap_and_paired_surface_chain_immediately"
