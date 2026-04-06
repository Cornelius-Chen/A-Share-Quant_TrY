from pathlib import Path

from a_share_quant.strategy.v127o_commercial_aerospace_new_primary_attribution_v1 import (
    V127OCommercialAerospaceNewPrimaryAttributionAnalyzer,
)


def test_v127o_new_primary_attribution() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127OCommercialAerospaceNewPrimaryAttributionAnalyzer(repo_root).analyze()

    assert report.summary["new_primary_variant"] == "veto_drag_trio_impulse_only"
    assert report.summary["equity_delta"] > 0
    assert report.summary["drawdown_delta"] < 0
