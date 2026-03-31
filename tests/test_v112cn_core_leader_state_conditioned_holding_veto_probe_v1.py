from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cn_core_leader_state_conditioned_holding_veto_probe_v1 import (
    V112CNCoreLeaderStateConditionedHoldingVetoProbeAnalyzer,
    load_json_report,
)


def test_v112cn_core_leader_state_conditioned_holding_veto_probe() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CNCoreLeaderStateConditionedHoldingVetoProbeAnalyzer()
    result = analyzer.analyze(
        bh_payload=load_json_report(repo_root / "reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json"),
        cm_payload=load_json_report(repo_root / "reports/analysis/v112cm_core_leader_half_life_probe_review_v1.json"),
    )
    summary = result.summary
    assert summary["holding_veto_count"] >= 2
    assert summary["beats_uniform_10d_return"] is True
    assert summary["beats_neutral_return"] is True
    assert summary["beats_neutral_drawdown"] is True
