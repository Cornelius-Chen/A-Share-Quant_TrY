from pathlib import Path

from a_share_quant.strategy.v134cz_commercial_aerospace_intraday_add_opening_checklist_v1 import (
    V134CZCommercialAerospaceIntradayAddOpeningChecklistV1Analyzer,
)


def test_v134cz_commercial_aerospace_intraday_add_opening_checklist_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CZCommercialAerospaceIntradayAddOpeningChecklistV1Analyzer(repo_root).analyze()

    assert result.summary["reduce_status"] == "frozen_mainline"
    assert result.summary["program_frontier_state"] == "deferred"
    assert result.summary["checklist_gate_count"] == 9
    assert any(
        row["opening_gate"] == "no_reduce_execution_authority_inheritance" and row["status"] == "mandatory"
        for row in result.checklist_rows
    )
