from pathlib import Path

from a_share_quant.strategy.v131q_commercial_aerospace_local_5min_resample_feasibility_audit_v1 import (
    V131QCommercialAerospaceLocal5MinResampleFeasibilityAuditAnalyzer,
)


def test_v131q_commercial_aerospace_local_5min_resample_feasibility_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131QCommercialAerospaceLocal5MinResampleFeasibilityAuditAnalyzer(repo_root).analyze()
    assert result.summary["manifest_row_count"] >= 4
    assert result.summary["ready_count"] == result.summary["manifest_row_count"]
    assert result.summary["local_5min_fully_ready"] is True
    assert all(int(row["five_minute_row_count"]) > 0 for row in result.feasibility_rows)
