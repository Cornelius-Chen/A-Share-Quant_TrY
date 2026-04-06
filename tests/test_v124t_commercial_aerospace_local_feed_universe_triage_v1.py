from pathlib import Path

from a_share_quant.strategy.v124t_commercial_aerospace_local_feed_universe_triage_v1 import (
    FEATURE_KEYS,
)


def test_v124t_feature_key_count() -> None:
    assert "trend_return_20" in FEATURE_KEYS
    assert len(FEATURE_KEYS) >= 6
