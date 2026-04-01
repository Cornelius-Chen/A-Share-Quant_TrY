from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113i_board_level_owner_labeling_protocol_v1 import (
    V113IBoardLevelOwnerLabelingProtocolAnalyzer,
    load_json_report,
)


def test_v113i_board_level_owner_labeling_protocol() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113IBoardLevelOwnerLabelingProtocolAnalyzer()
    result = analyzer.analyze(
        v113h_payload=load_json_report(repo_root / "reports/analysis/v113h_phase_charter_v1.json"),
        owner_board_level_only=True,
    )

    assert result.summary["owner_board_level_only"] is True
    assert result.summary["owner_scope_count"] == 3
    assert result.summary["assistant_scope_count"] == 4
