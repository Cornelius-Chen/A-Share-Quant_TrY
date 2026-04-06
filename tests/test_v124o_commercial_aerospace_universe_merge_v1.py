from pathlib import Path

from a_share_quant.strategy.v124o_commercial_aerospace_universe_merge_v1 import (
    V124OCommercialAerospaceUniverseMergeAnalyzer,
)


def test_v124o_merge_produces_superset() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124OCommercialAerospaceUniverseMergeAnalyzer(repo_root).analyze()

    assert result.summary["merged_count"] >= result.summary["base_count"]
    symbols = {row["symbol"] for row in result.merged_rows}
    assert "002085" in symbols
    assert "300900" in symbols
