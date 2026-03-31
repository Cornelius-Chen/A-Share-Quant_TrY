from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cj_neutral_packaging_control_injection_replay_v1 import (
    V112CJNeutralPackagingControlInjectionReplayAnalyzer,
    load_json_report,
)


def test_v112cj_neutral_packaging_control_injection_replay() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CJNeutralPackagingControlInjectionReplayAnalyzer()
    result = analyzer.analyze(
        neutral_payload=load_json_report(repo_root / "reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json"),
        bp_payload=load_json_report(repo_root / "reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json"),
        bz_payload=load_json_report(repo_root / "reports/analysis/v112bz_enabler_family_band_calibration_review_v1.json"),
        cf_payload=load_json_report(repo_root / "reports/analysis/v112cf_packaging_veto_derisk_boundary_refinement_review_v1.json"),
        ch_payload=load_json_report(repo_root / "reports/analysis/v112ch_packaging_mainline_template_freeze_v1.json"),
    )

    summary = result.summary
    assert summary["realized_path_changed"] is False
    assert summary["neutral_packaging_trade_count"] == 0
    assert summary["packaging_window_count"] > 0
    assert summary["packaging_window_missed_eligibility_rate"] >= 0.5
