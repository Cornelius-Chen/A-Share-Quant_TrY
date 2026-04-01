from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114f_multi_board_autonomous_research_orchestrator_protocol_v1 import (
    V114FMultiBoardAutonomousResearchOrchestratorProtocolAnalyzer,
)


def test_v114f_multi_board_autonomous_research_orchestrator_protocol() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114FMultiBoardAutonomousResearchOrchestratorProtocolAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        default_phase_version="v1_board_research_autonomous",
        board_queue=["CPO"],
    )

    assert result.summary["board_queue_count"] == 1
    assert result.summary["phase_count"] == 8
    assert result.summary["autonomous_posture"] == "run_until_terminal_status_per_board_without_manual_reprompt"

