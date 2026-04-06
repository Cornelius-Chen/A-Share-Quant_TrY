from pathlib import Path

from a_share_quant.strategy.v132p_commercial_aerospace_op_local_1min_shadow_benefit_triage_v1 import (
    V132PCommercialAerospaceOPLocal1MinShadowBenefitTriageAnalyzer,
)


def test_v132p_local_1min_shadow_benefit_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132PCommercialAerospaceOPLocal1MinShadowBenefitTriageAnalyzer(repo_root).analyze()

    assert report.summary["flagged_execution_share"] > 0.0
    assert report.summary["flagged_adverse_notional_share"] >= 0.0
    assert report.triage_rows[1]["status"] == "retain_unchanged"
