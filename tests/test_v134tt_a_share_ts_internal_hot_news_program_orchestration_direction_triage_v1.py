from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134tt_a_share_ts_internal_hot_news_program_orchestration_direction_triage_v1 import (
    V134TTAShareTSInternalHotNewsProgramOrchestrationDirectionTriageV1Analyzer,
)


def test_v134tt_program_orchestration_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TTAShareTSInternalHotNewsProgramOrchestrationDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["packet_row_count"] == 1
    assert "orchestration-packet" in report.summary["authoritative_status"]


def test_v134tt_program_orchestration_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TTAShareTSInternalHotNewsProgramOrchestrationDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
