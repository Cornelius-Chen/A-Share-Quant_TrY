from pathlib import Path

from a_share_quant.strategy.v127g_commercial_aerospace_primary_reference_attribution_v1 import (
    V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer,
)


def test_v127g_primary_reference_attribution_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer(repo_root).analyze()
    assert result.summary["primary_vs_v126o_equity_delta"] > 0
    assert result.summary["primary_vs_v126o_drawdown_delta"] < 0
    assert len(result.variant_rows) == 4
    assert len(result.drawdown_compare_rows) >= 4
