from a_share_quant.strategy.v123x_cpo_uvw_control_integration_triage_v1 import (
    V123XCpoUvwControlIntegrationTriageAnalyzer,
)


def test_v123x_freezes_riskoff_execution_downgrade() -> None:
    result = V123XCpoUvwControlIntegrationTriageAnalyzer().analyze()
    assert result.summary["authoritative_status"] == "downgrade_riskoff_execution_use"
    assert result.summary["majority_vote"]["downgrade_riskoff_execution_use"] == 3
