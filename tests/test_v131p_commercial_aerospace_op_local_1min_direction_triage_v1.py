from pathlib import Path

from a_share_quant.strategy.v131p_commercial_aerospace_op_local_1min_direction_triage_v1 import (
    V131PCommercialAerospaceOPLocal1MinDirectionTriageAnalyzer,
)


def test_v131p_commercial_aerospace_op_local_1min_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131PCommercialAerospaceOPLocal1MinDirectionTriageAnalyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "commercial_aerospace_local_1min_override_branch_unblocked"
    )
