from pathlib import Path

from a_share_quant.strategy.v134fy_commercial_aerospace_fx_positive_ranking_direction_triage_v1 import (
    V134FYCommercialAerospaceFXPositiveRankingDirectionTriageV1Analyzer,
)


def test_v134fy_commercial_aerospace_fx_positive_ranking_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FYCommercialAerospaceFXPositiveRankingDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_active_wave_exclusion_but_block_positive_daily_ranker_promotion"
    )
