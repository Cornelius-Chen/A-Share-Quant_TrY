from __future__ import annotations

from a_share_quant.strategy.next_batch_refresh_readiness import (
    NextBatchRefreshReadinessAnalyzer,
)


def test_next_batch_refresh_readiness_waits_when_v11_and_v2_seed_are_bounded() -> None:
    v11_continuation = {"summary": {"do_continue_current_specialist_loop": False}}
    v2_seed_continuation = {"summary": {"do_continue_current_v2_seed_replay": False}}
    specialist_payload = {
        "specialist_summaries": [
            {"candidate_name": "baseline_expansion_branch", "opportunity_count": 11, "top_datasets": ["market_research_v2_seed"]},
            {"candidate_name": "theme_strict_quality_branch", "opportunity_count": 10, "top_datasets": ["market_research_v1"]},
        ]
    }

    result = NextBatchRefreshReadinessAnalyzer().analyze(
        v11_continuation=v11_continuation,
        v2_seed_continuation=v2_seed_continuation,
        specialist_payload=specialist_payload,
        v2_seed_plan_text="market_research_v2_seed is a secondary specialist substrate",
    )

    assert result.summary["v11_current_loop_paused"] is True
    assert result.summary["v2_seed_local_loop_paused"] is True
    assert result.summary["v2_seed_secondary_substrate_status"] is True
    assert result.summary["do_open_market_research_v2_refresh_now"] is False
