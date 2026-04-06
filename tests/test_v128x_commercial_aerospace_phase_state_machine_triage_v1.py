from pathlib import Path

from a_share_quant.strategy.v128x_commercial_aerospace_phase_state_machine_triage_v1 import (
    V128XCommercialAerospacePhaseStateMachineTriageAnalyzer,
)


def test_v128x_commercial_aerospace_phase_state_machine_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128XCommercialAerospacePhaseStateMachineTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == "retain_probe_full_pre_full_de_risk_state_machine_for_translation"
    assert int(result.summary["full_pre_count"]) == 45
    assert int(result.summary["full_count"]) == 36
