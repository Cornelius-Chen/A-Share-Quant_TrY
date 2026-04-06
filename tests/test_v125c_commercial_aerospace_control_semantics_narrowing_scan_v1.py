from pathlib import Path

from a_share_quant.strategy.v125c_commercial_aerospace_control_semantics_narrowing_scan_v1 import (
    V125CCommercialAerospaceControlSemanticsNarrowingScanAnalyzer,
)


def test_v125c_has_variants() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125CCommercialAerospaceControlSemanticsNarrowingScanAnalyzer(repo_root).analyze()
    assert result.summary["variant_count"] >= 3
