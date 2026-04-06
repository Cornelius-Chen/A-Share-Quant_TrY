from pathlib import Path

from a_share_quant.strategy.v131t_commercial_aerospace_st_local_5min_override_triage_v1 import (
    V131TCommercialAerospaceSTLocal5MinOverrideTriageAnalyzer,
)


def test_v131t_commercial_aerospace_st_local_5min_override_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131TCommercialAerospaceSTLocal5MinOverrideTriageAnalyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "retain_commercial_aerospace_local_5min_override_prototype_as_governed_supervision"
    )
