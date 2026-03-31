from pathlib import Path

from a_share_quant.strategy.v112an_phase_check_v1 import (
    V112ANPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112an_phase_check_keeps_next_move_manual() -> None:
    analyzer = V112ANPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112an_phase_charter_v1.json")),
        result_review_payload=load_json_report(
            Path("reports/analysis/v112an_cpo_core_skeleton_pilot_result_review_v1.json")
        ),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["correction_bucket_count"] > 0
