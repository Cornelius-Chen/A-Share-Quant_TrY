from __future__ import annotations

from a_share_quant.strategy.v112o_optical_link_study_scope_v1 import (
    V112OOpticalLinkStudyScopeAnalyzer,
)


def test_v112o_study_scope_preserves_validated_and_review_only_candidates() -> None:
    result = V112OOpticalLinkStudyScopeAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112o_now": True}},
        pilot_dataset_payload={
            "dataset_rows": [
                {"symbol": "300308"},
                {"symbol": "300502"},
                {"symbol": "300394"},
            ]
        },
    )

    assert result.summary["validated_local_seed_count"] == 3
    assert result.summary["review_only_adjacent_candidate_count"] >= 4
    assert result.summary["bounded_study_dimension_count"] >= 6
