from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cu_packaging_admission_mode_promotion_review_v1 import (
    V112CUPackagingAdmissionModePromotionReviewAnalyzer,
    load_json_report,
)


def test_v112cu_packaging_admission_mode_promotion_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CUPackagingAdmissionModePromotionReviewAnalyzer()
    result = analyzer.analyze(
        ch_payload=load_json_report(repo_root / "reports/analysis/v112ch_packaging_mainline_template_freeze_v1.json"),
        cs_payload=load_json_report(repo_root / "reports/analysis/v112cs_core_residual_stack_status_freeze_v1.json"),
        ct_payload=load_json_report(repo_root / "reports/analysis/v112ct_packaging_eligibility_admission_probe_v1.json"),
    )
    summary = result.summary
    assert summary["promotion_ready"] is True
    assert summary["promotion_posture"] == "cluster_mainline_admission_extension_candidate"
    full_row = next(row for row in result.promotion_rows if row["promotion_target"] == "packaging_full_20d_admission_mode")
    assert full_row["beats_neutral_return"] is True
    assert full_row["beats_neutral_drawdown"] is True
