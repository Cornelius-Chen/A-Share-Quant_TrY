from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cq_high_beta_core_derisk_calibration_refinement_review_v1 import (
    V112CQHighBetaCoreDeriskCalibrationRefinementReviewAnalyzer,
    load_json_report,
)


def test_v112cq_high_beta_core_derisk_calibration_refinement_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CQHighBetaCoreDeriskCalibrationRefinementReviewAnalyzer()
    result = analyzer.analyze(
        co_payload=load_json_report(repo_root / "reports/analysis/v112co_high_beta_core_derisk_probe_review_v1.json"),
        cp_payload=load_json_report(repo_root / "reports/analysis/v112cp_neutral_core_residual_control_injection_replay_v1.json"),
    )
    summary = result.summary
    assert summary["band_count"] == 2
    assert summary["mild_band_neutral_safe"] is True
    assert summary["strong_band_beats_evidence_both"] is True
    assert summary["combined_replay_ready_after_split"] is False
