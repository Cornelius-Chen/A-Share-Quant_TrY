from pathlib import Path

from a_share_quant.strategy.v112br_phase_check_v1 import (
    V112BRPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112br_phase_check_accepts_completed_resonance_report() -> None:
    analyzer = V112BRPhaseCheckAnalyzer()
    result = analyzer.analyze(
        resonance_payload=load_json_report(Path("reports/analysis/v112br_state_representation_and_resonance_discovery_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
