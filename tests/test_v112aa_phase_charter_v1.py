from pathlib import Path

from a_share_quant.strategy.v112aa_phase_charter_v1 import (
    V112AAPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112aa_phase_charter_opens_after_v112z_reconstruction() -> None:
    analyzer = V112AAPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112z_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json"))
    )
    assert result.summary["do_open_v112aa_now"] is True
