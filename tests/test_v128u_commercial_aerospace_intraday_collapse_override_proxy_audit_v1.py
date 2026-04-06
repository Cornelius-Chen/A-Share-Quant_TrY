from pathlib import Path

from a_share_quant.strategy.v128u_commercial_aerospace_intraday_collapse_override_proxy_audit_v1 import (
    V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditAnalyzer,
)


def test_v128u_commercial_aerospace_intraday_collapse_override_proxy_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditAnalyzer(repo_root).analyze()

    assert int(result.summary["proxy_hit_order_count"]) == 2
    assert round(float(result.summary["retained_failure_coverage_rate"]), 8) == 1.0
    assert int(result.summary["watch_only_trigger_count"]) == 0

    proxy_ids = {f"{row['execution_trade_date']}_{row['symbol']}" for row in result.proxy_hit_rows}
    assert "20260113_601698" in proxy_ids
    assert "20260126_300342" in proxy_ids

    csv_path = repo_root / result.summary["proxy_hits_csv"]
    assert csv_path.exists()
