from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112co_high_beta_core_derisk_probe_review_v1 import (
    V112COHighBetaCoreDeriskProbeReviewAnalyzer,
    load_json_report,
)


def test_v112co_high_beta_core_derisk_probe_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112COHighBetaCoreDeriskProbeReviewAnalyzer()
    result = analyzer.analyze(
        bh_payload=load_json_report(repo_root / "reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json"),
        cl_payload=load_json_report(repo_root / "reports/analysis/v112cl_core_residual_control_probe_review_v1.json"),
    )
    summary = result.summary
    assert summary["de_risk_count"] >= 1
    assert summary["beats_evidence_baseline_return"] is True
    assert summary["beats_evidence_baseline_drawdown"] is True
    assert summary["neutral_realized_path_changed"] is True
    assert summary["promotable_into_neutral_now"] is True
    assert summary["neutral_symbol_return_delta"] > -0.1
