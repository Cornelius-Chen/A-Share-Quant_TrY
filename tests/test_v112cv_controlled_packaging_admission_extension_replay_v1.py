from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cv_controlled_packaging_admission_extension_replay_v1 import (
    V112CVControlledPackagingAdmissionExtensionReplayAnalyzer,
    load_json_report,
)


def test_v112cv_controlled_packaging_admission_extension_replay() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CVControlledPackagingAdmissionExtensionReplayAnalyzer()
    result = analyzer.analyze(
        bh_payload=load_json_report(repo_root / "reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json"),
        ct_payload=load_json_report(repo_root / "reports/analysis/v112ct_packaging_eligibility_admission_probe_v1.json"),
        cu_payload=load_json_report(repo_root / "reports/analysis/v112cu_packaging_admission_mode_promotion_review_v1.json"),
    )
    summary = result.summary
    assert summary["extension_replay_ready"] is True
    assert summary["displaced_neutral_trade_count"] == 1
    assert round(summary["return_delta_vs_neutral"], 4) == 0.9954
    assert round(summary["drawdown_delta_vs_neutral"], 4) == 0.028
