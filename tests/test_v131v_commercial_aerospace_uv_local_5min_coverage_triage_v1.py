from pathlib import Path

from a_share_quant.strategy.v131v_commercial_aerospace_uv_local_5min_coverage_triage_v1 import (
    V131VCommercialAerospaceUVLocal5MinCoverageTriageAnalyzer,
)


def test_v131v_local_5min_coverage_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131VCommercialAerospaceUVLocal5MinCoverageTriageAnalyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_local_5min_override_prototype_as_narrow_governed_supervision_with_false_positive_bounds_documented"
    )
    assert result.summary["non_override_flagged_count"] == 2
    assert result.summary["clean_control_hit_count"] == 0
