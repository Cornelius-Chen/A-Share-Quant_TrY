from pathlib import Path

from a_share_quant.strategy.v131h_commercial_aerospace_intraday_collection_manifest_v1 import (
    V131HCommercialAerospaceIntradayCollectionManifestAnalyzer,
)


def test_v131h_commercial_aerospace_intraday_collection_manifest_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131HCommercialAerospaceIntradayCollectionManifestAnalyzer(repo_root).analyze()

    assert result.summary["manifest_row_count"] == 4
    assert result.summary["high_priority_count"] == 2
    assert any(row["symbol"] == "601698" for row in result.manifest_rows)
