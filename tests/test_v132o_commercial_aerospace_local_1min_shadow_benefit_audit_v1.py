from pathlib import Path

from a_share_quant.strategy.v132o_commercial_aerospace_local_1min_shadow_benefit_audit_v1 import (
    V132OCommercialAerospaceLocal1MinShadowBenefitAuditAnalyzer,
)


def test_v132o_local_1min_shadow_benefit_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132OCommercialAerospaceLocal1MinShadowBenefitAuditAnalyzer(repo_root).analyze()

    assert report.summary["buy_execution_row_count"] == 55
    assert report.summary["flagged_execution_count"] == 6
    assert len(report.tier_rows) == 3
    assert report.summary["flagged_negative_forward_notional_share"] >= 0.0

