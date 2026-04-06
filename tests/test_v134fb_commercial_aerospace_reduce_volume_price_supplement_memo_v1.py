from pathlib import Path

from a_share_quant.strategy.v134fb_commercial_aerospace_reduce_volume_price_supplement_memo_v1 import (
    V134FBCommercialAerospaceReduceVolumePriceSupplementMemoV1Analyzer,
)


def test_v134fb_commercial_aerospace_reduce_volume_price_supplement_memo_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FBCommercialAerospaceReduceVolumePriceSupplementMemoV1Analyzer(repo_root).analyze()

    assert result.summary["strongest_reduce_volume_price_feature"] == "post_reversal_up_amount_share"
    assert result.summary["best_local_veto_up_share_threshold"] == 0.45
    assert result.summary["reduce_execution_blocker_count"] == 4
