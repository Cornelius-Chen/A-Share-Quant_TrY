from pathlib import Path

from a_share_quant.strategy.v113e_phase_closure_check_v1 import (
    V113EPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v113e_phase_closure_check_v1_blocks_auto_expansion() -> None:
    result = V113EPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v113e_phase_check_v1.json"))
    )
    assert result.summary["allow_auto_execution_now"] is False
    assert result.summary["allow_auto_signal_now"] is False
    assert result.summary["allow_auto_multi_archetype_expansion_now"] is False
