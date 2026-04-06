from pathlib import Path

from a_share_quant.strategy.v134eq_commercial_aerospace_ep_add_label_direction_triage_v1 import (
    V134EQCommercialAerospaceEPAddLabelDirectionTriageV1Analyzer,
)


def test_v134eq_commercial_aerospace_ep_add_label_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EQCommercialAerospaceEPAddLabelDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "freeze_intraday_add_tiered_label_specification_and_shift_next_to_local_add_pattern_envelope_audit"
    )
    assert result.summary["label_tier_count"] == 4
