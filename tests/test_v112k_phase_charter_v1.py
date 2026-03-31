from pathlib import Path

from a_share_quant.strategy.v112k_phase_charter_v1 import (
    V112KPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112k_phase_charter_v1_opens_only_from_high_level_consolidation_follow_up() -> None:
    result = V112KPhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path("reports/analysis/v112j_phase_closure_check_v1.json"))
    )
    assert result.summary["acceptance_posture"] == "open_v112k_high_level_consolidation_candidate_substate_drafting"
    assert result.summary["ready_for_drafting_next"] is True

