from a_share_quant.strategy.v124n_commercial_aerospace_universe_expansion_wave2_v1 import (
    V124NCommercialAerospaceUniverseExpansionWave2Analyzer,
)


def test_v124n_wave2_adds_confidence_tagged_names() -> None:
    result = V124NCommercialAerospaceUniverseExpansionWave2Analyzer().analyze()

    assert result.summary["added_count"] >= 10
    names = {row["symbol"]: row for row in result.added_rows}
    assert names["300900"]["group"] == "卖铲组"
    assert names["603131"]["group"] == "概念助推组"
    assert result.summary["high_confidence_added_count"] >= 5
