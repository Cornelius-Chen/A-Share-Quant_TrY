from pathlib import Path

from a_share_quant.strategy.v132w_commercial_aerospace_governance_stack_refresh_v3 import (
    V132WCommercialAerospaceGovernanceStackRefreshV3Analyzer,
)


def test_v132w_governance_stack_refresh_v3() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132WCommercialAerospaceGovernanceStackRefreshV3Analyzer(repo_root).analyze()

    assert report.summary["governance_layer_count"] >= 11
    assert any(row["layer"] == "local_1min_state_transition_governance" for row in report.governance_rows)

