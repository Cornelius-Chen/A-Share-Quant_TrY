from pathlib import Path

from a_share_quant.strategy.v134ep_commercial_aerospace_intraday_add_tiered_label_specification_v1 import (
    V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Analyzer,
)


def test_v134ep_commercial_aerospace_intraday_add_tiered_label_specification_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Analyzer(repo_root).analyze()

    assert result.summary["registry_row_count"] == 55
    assert result.summary["label_tier_count"] == 4

    tier_counts = {row["label_tier"]: row["session_count"] for row in result.tier_rows}
    assert tier_counts["allowed_preheat_probe_add"] == 33
    assert tier_counts["allowed_preheat_full_add"] == 16
    assert tier_counts["failed_impulse_chase_add"] == 2
    assert tier_counts["blocked_board_lockout_add"] == 4
