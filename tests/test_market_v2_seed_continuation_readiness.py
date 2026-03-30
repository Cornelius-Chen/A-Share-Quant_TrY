from __future__ import annotations

from a_share_quant.strategy.market_v2_seed_continuation_readiness import (
    MarketV2SeedContinuationReadinessAnalyzer,
)


def test_market_v2_seed_continuation_readiness_pauses_after_two_closed_lanes() -> None:
    q4_payload = {"summary": {"do_continue_q4_capture_replay": False}}
    q3_payload = {"summary": {"do_continue_q3_drawdown_replay": False}}
    audit_payload = {"summary": {"baseline_ready": True, "derived_ready_count": 3}}
    specialist_payload = {
        "summary": {"top_specialist_by_opportunity_count": "baseline_expansion_branch"},
        "specialist_summaries": [
            {"candidate_name": "baseline_expansion_branch", "top_datasets": ["market_research_v2_seed"]},
            {"candidate_name": "theme_strict_quality_branch", "top_datasets": ["market_research_v1"]},
        ],
    }

    result = MarketV2SeedContinuationReadinessAnalyzer().analyze(
        q4_capture_acceptance=q4_payload,
        q3_drawdown_acceptance=q3_payload,
        audit_payload=audit_payload,
        specialist_payload=specialist_payload,
    )

    assert result.summary["all_open_v2_seed_lanes_closed"] is True
    assert result.summary["v2_seed_contributes_specialist_pockets"] is True
    assert result.summary["do_continue_current_v2_seed_replay"] is False
