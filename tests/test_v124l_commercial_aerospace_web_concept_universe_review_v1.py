from a_share_quant.strategy.v124l_commercial_aerospace_web_concept_universe_review_v1 import (
    V124LCommercialAerospaceWebConceptUniverseReviewAnalyzer,
)


def test_v124l_universe_review_keeps_user_named_names_and_shovel_names() -> None:
    result = V124LCommercialAerospaceWebConceptUniverseReviewAnalyzer().analyze()

    groups = {row["symbol"]: row["group"] for row in result.universe_rows}
    assert groups["002565"] == "概念助推组"
    assert groups["002202"] == "概念助推组"
    assert groups["600783"] == "概念助推组"
    assert groups["001208"] == "卖铲组"
    assert groups["001270"] == "卖铲组"
    assert groups["688270"] == "卖铲组"
    assert groups["603601"] == "概念助推组"
    assert groups["301306"] == "卖铲组"
    assert groups["002471"] == "概念助推组"
