from __future__ import annotations

from a_share_quant.strategy.v110a_phase_check_v1 import V110APhaseCheckAnalyzer


def test_v110a_phase_check_blocks_follow_on_probe() -> None:
    result = V110APhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v110a_now": True}},
        cross_family_probe_payload={
            "summary": {
                "candidate_count": 2,
                "admitted_case_count": 0,
                "successful_negative_probe": True,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "keep_v110a_single_probe_bounded_and_non_expanding"
    assert result.summary["open_follow_on_probe_now"] is False
