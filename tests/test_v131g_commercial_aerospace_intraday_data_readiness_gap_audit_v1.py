from pathlib import Path

from a_share_quant.strategy.v131g_commercial_aerospace_intraday_data_readiness_gap_audit_v1 import (
    V131GCommercialAerospaceIntradayDataReadinessGapAuditAnalyzer,
)


def test_v131g_commercial_aerospace_intraday_data_readiness_gap_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131GCommercialAerospaceIntradayDataReadinessGapAuditAnalyzer(repo_root).analyze()

    assert result.summary["required_intraday_symbol_count"] == 4
    assert result.summary["required_intraday_symbol_coverage_rate"] == 0.0
    assert result.summary["missing_required_symbol_count"] == 4
    assert "601698" in result.summary["missing_required_symbols"]
