from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114v_cpo_benchmark_integrity_review_v1 import (
    V114VCpoBenchmarkIntegrityReviewAnalyzer,
    load_json_report,
)


def test_v114v_cpo_benchmark_integrity_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114VCpoBenchmarkIntegrityReviewAnalyzer()
    result = analyzer.analyze(
        v112aa_payload=load_json_report(repo_root / "reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json"),
        v114t_payload=load_json_report(repo_root / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json"),
    )

    assert result.summary["board_benchmark_is_opportunity_ceiling"] is True
    assert result.summary["recommended_primary_comparison"] == "strategy_vs_action_coverage_proxy"
    assert len(result.benchmark_rows) == 3
