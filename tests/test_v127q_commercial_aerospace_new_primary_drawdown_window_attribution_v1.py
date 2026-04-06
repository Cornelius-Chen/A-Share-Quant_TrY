from pathlib import Path

from a_share_quant.strategy.v127q_commercial_aerospace_new_primary_drawdown_window_attribution_v1 import (
    V127QCommercialAerospaceNewPrimaryDrawdownWindowAttributionAnalyzer,
)


def test_v127q_new_primary_drawdown_window_attribution() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127QCommercialAerospaceNewPrimaryDrawdownWindowAttributionAnalyzer(repo_root).analyze()

    assert report.summary["new_primary_variant"] == "veto_drag_trio_impulse_only"
    assert report.summary["drawdown_delta"] < 0
    assert len(report.window_rows) >= 1
