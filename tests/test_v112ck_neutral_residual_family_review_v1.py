from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112ck_neutral_residual_family_review_v1 import (
    V112CKNeutralResidualFamilyReviewAnalyzer,
    load_json_report,
)


def test_v112ck_neutral_residual_family_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CKNeutralResidualFamilyReviewAnalyzer()
    result = analyzer.analyze(
        cj_payload=load_json_report(repo_root / "reports/analysis/v112cj_neutral_packaging_control_injection_replay_v1.json"),
    )

    summary = result.summary
    assert summary["packaging_injection_immediate_gain"] is False
    assert summary["residual_family_count"] >= 2
