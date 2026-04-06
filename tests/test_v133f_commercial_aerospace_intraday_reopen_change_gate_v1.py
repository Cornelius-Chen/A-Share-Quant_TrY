from pathlib import Path

from a_share_quant.strategy.v133f_commercial_aerospace_intraday_reopen_change_gate_v1 import (
    V133FCommercialAerospaceIntradayReopenChangeGateAnalyzer,
)


def test_v133f_intraday_reopen_change_gate_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133FCommercialAerospaceIntradayReopenChangeGateAnalyzer(repo_root).analyze()

    assert report.summary["artifact_count"] == 5
    assert report.summary["missing_artifact_count"] == 3
    assert report.summary["rerun_required"] is False

