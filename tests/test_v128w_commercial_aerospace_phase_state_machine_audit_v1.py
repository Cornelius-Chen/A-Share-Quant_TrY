from pathlib import Path

from a_share_quant.strategy.v128w_commercial_aerospace_phase_state_machine_audit_v1 import (
    V128WCommercialAerospacePhaseStateMachineAuditAnalyzer,
)


def test_v128w_commercial_aerospace_phase_state_machine_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128WCommercialAerospacePhaseStateMachineAuditAnalyzer(repo_root).analyze()

    assert int(result.summary["full_pre_count"]) == 45
    assert int(result.summary["full_count"]) == 36
    assert result.summary["full_pre_start"] == "20251121"
    assert result.summary["full_pre_end"] == "20251223"
    assert result.summary["full_start"] == "20251224"
    assert result.summary["full_end"] == "20260112"
    assert abs(float(result.summary["full_pre_forward_minus_full_forward"])) < 0.02

