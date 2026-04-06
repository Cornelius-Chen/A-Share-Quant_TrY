from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134tj_a_share_ti_internal_hot_news_program_runtime_execution_direction_triage_v1 import (
    V134TJAShareTIInternalHotNewsProgramRuntimeExecutionDirectionTriageV1Analyzer,
)


def test_v134tj_runtime_execution_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TJAShareTIInternalHotNewsProgramRuntimeExecutionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["contract_row_count"] == 1
    assert "runtime-execution_contract" in report.summary["authoritative_status"]


def test_v134tj_runtime_execution_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TJAShareTIInternalHotNewsProgramRuntimeExecutionDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
