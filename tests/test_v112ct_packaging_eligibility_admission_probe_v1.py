from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112ct_packaging_eligibility_admission_probe_v1 import (
    V112CTPackagingEligibilityAdmissionProbeAnalyzer,
    load_json_report,
)


def test_v112ct_packaging_eligibility_admission_probe() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CTPackagingEligibilityAdmissionProbeAnalyzer()
    result = analyzer.analyze(
        bh_payload=load_json_report(repo_root / "reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json"),
        cj_payload=load_json_report(repo_root / "reports/analysis/v112cj_neutral_packaging_control_injection_replay_v1.json"),
    )
    summary = result.summary
    assert summary["preferred_mode"] == "full_20d_admission"
    full_row = next(row for row in result.mode_rows if row["mode_name"] == "full_20d_admission")
    assert full_row["beats_neutral_return"] is True
    assert full_row["beats_neutral_drawdown"] is True
