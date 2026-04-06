from a_share_quant.strategy.v123t_cpo_qrs_daily_residual_triage_v1 import (
    V123TCpoQrsDailyResidualTriageAnalyzer,
)


def test_v123t_freezes_residual_branch_as_soft_component() -> None:
    result = V123TCpoQrsDailyResidualTriageAnalyzer().analyze()
    assert result.summary["authoritative_status"] == "soft_component"
    assert result.summary["majority_vote"]["soft_component"] == 3
