from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113j_board_research_world_model_protocol_v1 import (
    V113JBoardResearchWorldModelProtocolAnalyzer,
    load_json_report,
)


def test_v113j_board_research_world_model_protocol() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113JBoardResearchWorldModelProtocolAnalyzer()
    result = analyzer.analyze(
        v113i_payload=load_json_report(repo_root / "reports/analysis/v113i_board_level_owner_labeling_protocol_v1.json"),
        world_model_teaching_approved=True,
    )

    assert result.summary["layer_count"] == 4
    assert result.summary["teaching_mode"] == "teach_mechanism_not_answer"
