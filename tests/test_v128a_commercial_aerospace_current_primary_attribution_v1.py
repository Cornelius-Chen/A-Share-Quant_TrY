from pathlib import Path

from a_share_quant.strategy.v128a_commercial_aerospace_current_primary_attribution_v1 import (
    V128ACommercialAerospaceCurrentPrimaryAttributionAnalyzer,
)


def test_v128a_current_primary_attribution() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128ACommercialAerospaceCurrentPrimaryAttributionAnalyzer(repo_root).analyze()

    assert report.summary["new_primary_variant"] == "window_riskoff_full_weakdrift_075_impulse_half"
    assert len(report.variant_rows) == 2
    assert len(report.drawdown_rows) >= 1
