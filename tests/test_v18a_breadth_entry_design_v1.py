from __future__ import annotations

from a_share_quant.strategy.v18a_breadth_entry_design_v1 import (
    V18ABreadthEntryDesignAnalyzer,
)


def test_v18a_breadth_entry_design_freezes_minimum_lawful_entries() -> None:
    result = V18ABreadthEntryDesignAnalyzer().analyze(
        sample_breadth_protocol_payload={
            "summary": {"ready_for_breadth_entry_design_next": True},
            "protocol": {
                "target_feature_rows": [
                    {
                        "feature_name": "single_pulse_support",
                        "minimum_evidence_path": "bounded_multi_sample_review",
                    },
                    {
                        "feature_name": "policy_followthrough_support",
                        "minimum_evidence_path": "bounded_additional_followthrough_case_review",
                    },
                ]
            },
        }
    )

    assert result.summary["acceptance_posture"] == "freeze_v18a_breadth_entry_design_v1"
    assert result.summary["entry_row_count"] == 2
    assert result.summary["allow_unbounded_sample_collection_now"] is False
    assert result.summary["ready_for_v18a_phase_check_next"] is True
