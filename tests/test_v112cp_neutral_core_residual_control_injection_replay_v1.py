from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cp_neutral_core_residual_control_injection_replay_v1 import (
    V112CPNeutralCoreResidualControlInjectionReplayAnalyzer,
    load_json_report,
)


def test_v112cp_neutral_core_residual_control_injection_replay() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CPNeutralCoreResidualControlInjectionReplayAnalyzer()
    result = analyzer.analyze(
        bh_payload=load_json_report(repo_root / "reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json"),
        cn_payload=load_json_report(repo_root / "reports/analysis/v112cn_core_leader_state_conditioned_holding_veto_probe_v1.json"),
        co_payload=load_json_report(repo_root / "reports/analysis/v112co_high_beta_core_derisk_probe_review_v1.json"),
    )
    summary = result.summary
    assert summary["holding_veto_count"] >= 1
    assert summary["de_risk_count"] >= 1
    assert summary["beats_neutral_drawdown"] is True
    assert summary["return_delta_vs_neutral"] > -0.05
    assert summary["combined_promotion_ready"] is False
