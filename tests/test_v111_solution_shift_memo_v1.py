from __future__ import annotations

from a_share_quant.strategy.v111_solution_shift_memo_v1 import V111SolutionShiftMemoAnalyzer


def test_v111_solution_shift_memo_selects_data_acquisition_after_exhausted_pool() -> None:
    result = V111SolutionShiftMemoAnalyzer().analyze(
        v110a_phase_closure_payload={"summary": {"enter_v110a_waiting_state_now": True}},
        v110a_cross_family_probe_payload={"summary": {"successful_negative_probe": True}},
    )

    assert result.summary["acceptance_posture"] == "emit_solution_shift_memo_as_data_acquisition_plan"
    assert result.memo["memo_type"] == "Data Acquisition Plan"
    assert result.summary["do_open_v111_now"] is True
