from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cm_core_leader_half_life_probe_review_v1 import (
    V112CMCoreLeaderHalfLifeProbeReviewAnalyzer,
    load_json_report,
)


def test_v112cm_core_leader_half_life_probe_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CMCoreLeaderHalfLifeProbeReviewAnalyzer()
    result = analyzer.analyze(
        bh_payload=load_json_report(repo_root / "reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json"),
    )
    summary = result.summary
    assert summary["simple_half_life_cut_sufficient"] is False
    assert len(result.half_life_rows) == 4
