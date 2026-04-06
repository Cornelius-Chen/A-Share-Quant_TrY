from pathlib import Path

from a_share_quant.strategy.v134eh_commercial_aerospace_intraday_add_frontier_opening_v1 import (
    V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Analyzer,
)


def test_v134eh_commercial_aerospace_intraday_add_frontier_opening_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Analyzer(repo_root).analyze()

    assert result.summary["frontier_state"] == "opened_supervision_only"
    assert result.summary["first_build_step"] == "intraday_add_supervision_registry_v1"
    assert any(
        row["opening_stage"] == "reduce_authority" and row["status"] == "not_inherited"
        for row in result.opening_rows
    )
