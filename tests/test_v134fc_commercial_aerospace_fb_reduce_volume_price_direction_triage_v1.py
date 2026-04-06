from pathlib import Path

from a_share_quant.strategy.v134fc_commercial_aerospace_fb_reduce_volume_price_direction_triage_v1 import (
    V134FCCommercialAerospaceFBReduceVolumePriceDirectionTriageV1Analyzer,
)


def test_v134fc_commercial_aerospace_fb_reduce_volume_price_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FCCommercialAerospaceFBReduceVolumePriceDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "freeze_reduce_volume_price_supplement_inside_frozen_handoff_package"
    )
