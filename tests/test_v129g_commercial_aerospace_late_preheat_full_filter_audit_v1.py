from pathlib import Path

from a_share_quant.strategy.v129g_commercial_aerospace_late_preheat_full_filter_audit_v1 import (
    V129GCommercialAerospaceLatePreheatFullFilterAuditAnalyzer,
)


def test_v129g_commercial_aerospace_late_preheat_full_filter_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129GCommercialAerospaceLatePreheatFullFilterAuditAnalyzer(repo_root).analyze()

    assert len(result.variant_rows) == 7
    assert "best_variant" in result.summary
