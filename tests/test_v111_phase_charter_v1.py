from __future__ import annotations

from a_share_quant.strategy.v111_phase_charter_v1 import V111PhaseCharterAnalyzer


def test_v111_phase_charter_opens_exploration_layer_infrastructure_phase() -> None:
    result = V111PhaseCharterAnalyzer().analyze(
        solution_shift_memo_payload={
            "summary": {"do_open_v111_now": True},
            "memo": {"memo_type": "Data Acquisition Plan", "current_primary_bottleneck_category": "data_or_evidence_gap"},
        }
    )

    assert result.summary["acceptance_posture"] == "open_v111_sustained_catalyst_evidence_acquisition_infrastructure"
    assert result.summary["do_open_v111_now"] is True
    assert result.charter["exploration_layer_phase"] is True
