from __future__ import annotations

from a_share_quant.strategy.v113g_commercial_space_study_scope_v1 import (
    V113GCommercialSpaceStudyScopeAnalyzer,
)


def test_v113g_study_scope_preserves_validated_and_owner_named_candidates() -> None:
    result = V113GCommercialSpaceStudyScopeAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v113g_now": True}},
        pilot_object_pool_payload={
            "object_rows": [
                {"symbol": "002085"},
                {"symbol": "000738"},
                {"symbol": "600118"},
            ]
        },
    )

    assert result.summary["validated_local_seed_count"] == 3
    assert result.summary["owner_named_candidate_count"] >= 5
    assert result.summary["bounded_study_dimension_count"] >= 4
