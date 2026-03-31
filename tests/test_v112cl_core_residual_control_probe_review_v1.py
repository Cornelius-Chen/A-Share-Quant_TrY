from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cl_core_residual_control_probe_review_v1 import (
    V112CLCoreResidualControlProbeReviewAnalyzer,
    load_json_report,
)


def test_v112cl_core_residual_control_probe_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CLCoreResidualControlProbeReviewAnalyzer()
    result = analyzer.analyze(
        ck_payload=load_json_report(repo_root / "reports/analysis/v112ck_neutral_residual_family_review_v1.json"),
        bh_payload=load_json_report(repo_root / "reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json"),
        bk_payload=load_json_report(repo_root / "reports/analysis/v112bk_cpo_tree_ranker_search_v1.json"),
    )
    summary = result.summary
    assert summary["family_count"] >= 2
    assert summary["packaging_template_kept_frozen"] is True
