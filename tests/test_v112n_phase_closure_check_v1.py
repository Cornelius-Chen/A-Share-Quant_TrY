from pathlib import Path

from a_share_quant.strategy.v112n_phase_closure_check_v1 import V112NPhaseClosureCheckAnalyzer, load_json_report


def test_v112n_phase_closure_check_v1_blocks_auto_feature_promotion() -> None:
    result = V112NPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112n_phase_check_v1.json"))
    )
    assert result.summary["enter_v112n_waiting_state_now"] is True
    assert result.summary["allow_auto_feature_promotion_now"] is False
    assert result.summary["allow_auto_label_action_now"] is False
