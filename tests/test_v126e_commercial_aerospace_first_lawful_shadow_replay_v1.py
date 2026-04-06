from pathlib import Path

from a_share_quant.strategy.v126e_commercial_aerospace_first_lawful_shadow_replay_v1 import (
    V126ECommercialAerospaceFirstLawfulShadowReplayAnalyzer,
)


def test_v126e_runs_first_lawful_shadow_replay() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V126ECommercialAerospaceFirstLawfulShadowReplayAnalyzer(repo_root).analyze()
    assert result.summary["test_date_count"] > 0
