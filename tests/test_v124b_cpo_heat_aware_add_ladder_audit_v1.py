from pathlib import Path

from a_share_quant.strategy.v124b_cpo_heat_aware_add_ladder_audit_v1 import (
    V124BCpoHeatAwareAddLadderAuditAnalyzer,
)


def test_v124b_heat_add_ladder_variants_are_valid() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result, daily_rows = V124BCpoHeatAwareAddLadderAuditAnalyzer(repo_root=repo_root).analyze()

    assert result.summary["variant_count"] == 5
    assert len(daily_rows) > 100
    variant_names = {row["variant_name"] for row in result.variant_rows}
    assert "balanced_heat_reference" in variant_names
    assert all(row["final_equity"] > 0 for row in result.variant_rows)
    assert all(0.0 <= row["max_drawdown"] <= 1.0 for row in result.variant_rows)
