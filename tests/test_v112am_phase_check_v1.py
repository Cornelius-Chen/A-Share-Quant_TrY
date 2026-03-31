from pathlib import Path

from a_share_quant.strategy.v112am_phase_check_v1 import (
    V112AMPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112am_phase_check_keeps_training_closed() -> None:
    analyzer = V112AMPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112am_phase_charter_v1.json")),
        training_pilot_payload=load_json_report(
            Path("reports/analysis/v112am_cpo_extremely_small_core_skeleton_training_pilot_v1.json")
        ),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["allow_auto_signal_generation_now"] is False
    assert result.summary["target_count"] == 3
