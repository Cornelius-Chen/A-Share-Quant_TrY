from pathlib import Path

from a_share_quant.strategy.v133n_commercial_aerospace_intraday_execution_build_triage_v1 import (
    V133NCommercialAerospaceIntradayExecutionBuildTriageAnalyzer,
)


def test_v133n_commercial_aerospace_intraday_execution_build_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133NCommercialAerospaceIntradayExecutionBuildTriageAnalyzer(repo_root).analyze()

    assert report.summary["reviewer_count"] == 3
    assert report.summary["protocol_workstream_count"] == 3
    assert report.consensus_rows[0]["status"] == "approved_with_guardrails"
    assert "first_visible_ts" in report.consensus_rows[1]["detail"]
