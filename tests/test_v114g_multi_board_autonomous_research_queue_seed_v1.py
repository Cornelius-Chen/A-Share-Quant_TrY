from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114g_multi_board_autonomous_research_queue_seed_v1 import (
    V114GMultiBoardAutonomousResearchQueueSeedAnalyzer,
)


def test_v114g_multi_board_autonomous_research_queue_seed() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114GMultiBoardAutonomousResearchQueueSeedAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114f_payload=load_json_report(repo_root / "reports" / "analysis" / "v114f_multi_board_autonomous_research_orchestrator_protocol_v1.json"),
        board_queue=["CPO"],
    )

    assert result.summary["autonomous_queue_ready"] is True
    assert len(result.queue_rows) == 1
    assert result.queue_rows[0]["next_phase"] == "board_world_model"
