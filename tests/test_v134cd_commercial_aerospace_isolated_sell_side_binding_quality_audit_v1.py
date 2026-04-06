from pathlib import Path

from a_share_quant.strategy.v134cd_commercial_aerospace_isolated_sell_side_binding_quality_audit_v1 import (
    V134CDCommercialAerospaceIsolatedSellSideBindingQualityAuditV1Analyzer,
)


def test_v134cd_commercial_aerospace_isolated_sell_side_binding_quality_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CDCommercialAerospaceIsolatedSellSideBindingQualityAuditV1Analyzer(repo_root).analyze()

    assert result.summary["broader_hit_session_count"] == 24
    assert result.summary["executed_session_count"] == 12
    assert result.summary["clipped_reconciliation_count"] == 2
    assert result.summary["same_day_new_lots_protected_total"] >= 6000
    assert result.summary["best_symbol"] == "300342"
    assert result.summary["best_trigger_tier"] == "reversal_watch"
    assert any(
        row["symbol"] == "300342" and row["same_day_reduce_close_clipped_total"] > 0 for row in result.symbol_rows
    )
    assert any(row["trade_date"] == "20260120" and row["symbol"] == "300342" for row in result.clip_rows)
