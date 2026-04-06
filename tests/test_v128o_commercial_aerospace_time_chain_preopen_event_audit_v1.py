from pathlib import Path

from a_share_quant.strategy.v128o_commercial_aerospace_time_chain_preopen_event_audit_v1 import (
    V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer,
)


def test_v128o_commercial_aerospace_time_chain_preopen_event_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer(repo_root).analyze()

    assert result.summary["primary_variant"] == "tail_weakdrift_full"
    assert int(result.summary["suspicious_buy_order_count"]) == 0
    assert int(result.summary["adverse_execution_day_count"]) >= 0
    assert len(result.execution_day_rows) > 0
