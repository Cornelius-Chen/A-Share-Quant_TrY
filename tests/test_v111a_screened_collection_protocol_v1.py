from __future__ import annotations

from a_share_quant.strategy.v111a_screened_collection_protocol_v1 import (
    V111AScreenedCollectionProtocolAnalyzer,
)


def test_v111a_screened_collection_protocol_freezes_small_bounded_caps() -> None:
    result = V111AScreenedCollectionProtocolAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v111a_now": True}},
        v111_plan_payload={
            "plan": {
                "bounded_first_pilot_plan": {
                    "pilot_candidate_cap": 5,
                    "pilot_admission_cap": 2,
                    "pilot_priority_order": ["a", "b"],
                }
            }
        },
    )

    assert result.summary["candidate_cap"] == 5
    assert result.summary["admission_cap"] == 2
    assert result.summary["ready_for_screened_collection_next"] is True
