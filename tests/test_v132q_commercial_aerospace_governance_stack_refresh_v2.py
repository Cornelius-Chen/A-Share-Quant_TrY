from pathlib import Path

from a_share_quant.strategy.v132q_commercial_aerospace_governance_stack_refresh_v2 import (
    V132QCommercialAerospaceGovernanceStackRefreshV2Analyzer,
)


def test_v132q_governance_stack_refresh_v2() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132QCommercialAerospaceGovernanceStackRefreshV2Analyzer(repo_root).analyze()

    assert report.summary["governance_layer_count"] >= 10
    assert report.summary["current_primary_variant"] == "tail_weakdrift_full"
    assert any(row["layer"] == "local_1min_shadow_benefit_governance" for row in report.governance_rows)

