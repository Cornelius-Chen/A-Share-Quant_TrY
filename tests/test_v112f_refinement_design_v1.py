from __future__ import annotations

from a_share_quant.strategy.v112f_refinement_design_v1 import V112FRefinementDesignAnalyzer


def test_v112f_refinement_design_picks_feature_gap_as_primary() -> None:
    result = V112FRefinementDesignAnalyzer().analyze(
        phase_charter_payload={"summary": {"ready_for_refinement_design_next": True}},
        hotspot_review_payload={"summary": {"primary_reading": "baseline_is_overoptimistic_in_late_markup_and_high_level_consolidation"}},
        attribution_review_payload={
            "summary": {"most_useful_block_by_hotspot_impact": "catalyst_state"},
            "block_ablation_rows": [
                {
                    "ablated_block": "catalyst_state",
                    "false_positive_count_in_major_markup": 125,
                    "false_positive_count_in_high_level_consolidation": 53,
                }
            ],
        },
    )

    assert result.summary["primary_bottleneck_type"] == "feature_definition_or_non_redundancy_gap"
    assert result.summary["recommend_feature_refinement_first"] is True
    assert len(result.catalyst_state_refinement_rows) == 3
