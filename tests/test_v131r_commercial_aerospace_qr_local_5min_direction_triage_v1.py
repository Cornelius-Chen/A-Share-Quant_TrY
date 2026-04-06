from pathlib import Path

from a_share_quant.strategy.v131r_commercial_aerospace_qr_local_5min_direction_triage_v1 import (
    V131RCommercialAerospaceQRLocal5MinDirectionTriageAnalyzer,
)


def test_v131r_commercial_aerospace_qr_local_5min_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131RCommercialAerospaceQRLocal5MinDirectionTriageAnalyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "commercial_aerospace_local_5min_override_branch_unblocked"
    )
