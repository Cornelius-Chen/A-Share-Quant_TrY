from pathlib import Path

from a_share_quant.strategy.v123q_cpo_daily_residual_cash_floor_sensitivity_audit_v1 import (
    V123QCpoDailyResidualCashFloorSensitivityAuditAnalyzer,
)


def test_v123q_daily_residual_cash_floor_sensitivity_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V123QCpoDailyResidualCashFloorSensitivityAuditAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["cash_floor_count"] == 4
    assert result.summary["stable_cash_floor_count"] >= 2
