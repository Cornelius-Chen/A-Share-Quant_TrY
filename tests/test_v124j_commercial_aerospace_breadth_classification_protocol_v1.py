from a_share_quant.strategy.v124j_commercial_aerospace_breadth_classification_protocol_v1 import (
    V124JCommercialAerospaceBreadthClassificationProtocolAnalyzer,
)


def test_v124j_classification_keeps_broad_concept_names_out_of_direct_driver_tier() -> None:
    result = V124JCommercialAerospaceBreadthClassificationProtocolAnalyzer().analyze()

    assert result.summary["tier_count"] == 4
    assert result.summary["direct_driver_count"] == 3
    assert result.manual_watchlist_rows[0]["initial_classification"] == "tier_3_thematic_propagation_concepts"
    assert result.tier_rows[0]["symbols"] == ["002085", "000738", "600118"]
