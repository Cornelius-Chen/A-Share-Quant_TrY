from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cr_high_beta_core_derisk_replay_split_v1 import (
    V112CRHighBetaCoreDeriskReplaySplitAnalyzer,
    load_json_report,
)


def test_v112cr_high_beta_core_derisk_replay_split() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CRHighBetaCoreDeriskReplaySplitAnalyzer()
    result = analyzer.analyze(
        bh_payload=load_json_report(repo_root / "reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json"),
        cq_payload=load_json_report(repo_root / "reports/analysis/v112cq_high_beta_core_derisk_calibration_refinement_review_v1.json"),
    )
    summary = result.summary
    assert summary["preferred_band"] == "neutral_safe_mild_derisk_band"
    assert summary["mild_return_delta_vs_neutral"] >= summary["strong_return_delta_vs_neutral"]
    assert summary["mild_drawdown_delta_vs_neutral"] >= summary["strong_drawdown_delta_vs_neutral"]
