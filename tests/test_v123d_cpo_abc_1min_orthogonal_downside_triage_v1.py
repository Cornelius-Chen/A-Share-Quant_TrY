from pathlib import Path

from a_share_quant.strategy.v123d_cpo_abc_1min_orthogonal_downside_triage_v1 import (
    V123DCpoAbc1MinOrthogonalDownsideTriageAnalyzer,
)


def test_v123d_freezes_soft_component_majority() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V123DCpoAbc1MinOrthogonalDownsideTriageAnalyzer().analyze()
    assert result.summary["authoritative_status"] == "soft_component"
    assert result.summary["majority_vote"]["soft_component"] == 2

