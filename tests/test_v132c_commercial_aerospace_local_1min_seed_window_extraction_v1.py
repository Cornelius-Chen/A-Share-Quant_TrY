from pathlib import Path

from a_share_quant.strategy.v132c_commercial_aerospace_local_1min_seed_window_extraction_v1 import (
    V132CCommercialAerospaceLocal1MinSeedWindowExtractionAnalyzer,
)


def test_v132c_local_1min_seed_window_extraction() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132CCommercialAerospaceLocal1MinSeedWindowExtractionAnalyzer(repo_root).analyze()

    assert result.summary["registry_session_count"] == 6
    assert result.summary["seed_window_row_count"] == 360
    assert result.summary["minutes_per_session"] == 60

