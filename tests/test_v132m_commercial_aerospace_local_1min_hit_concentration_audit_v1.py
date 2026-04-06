from pathlib import Path

from a_share_quant.strategy.v132m_commercial_aerospace_local_1min_hit_concentration_audit_v1 import (
    V132MCommercialAerospaceLocal1MinHitConcentrationAuditAnalyzer,
)


def test_v132m_local_1min_hit_concentration_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132MCommercialAerospaceLocal1MinHitConcentrationAuditAnalyzer(repo_root).analyze()

    assert result.summary["expanded_hit_count"] == 24
    assert result.summary["unique_hit_trade_date_count"] > 0
    assert result.summary["main_window"] == "20260112->20260212"

