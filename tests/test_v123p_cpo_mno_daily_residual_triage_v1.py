from a_share_quant.strategy.v123p_cpo_mno_daily_residual_triage_v1 import (
    V123PCpoMnoDailyResidualTriageAnalyzer,
)


def test_v123p_freezes_daily_residual_branch_as_candidate_only() -> None:
    result = V123PCpoMnoDailyResidualTriageAnalyzer().analyze()
    assert result.summary["authoritative_status"] == "candidate_only"
    assert result.summary["majority_vote"]["candidate_only"] == 2
