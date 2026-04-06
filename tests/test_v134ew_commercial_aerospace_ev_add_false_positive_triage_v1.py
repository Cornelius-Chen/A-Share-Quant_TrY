from pathlib import Path

from a_share_quant.strategy.v134ew_commercial_aerospace_ev_add_false_positive_triage_v1 import (
    V134EWCommercialAerospaceEVAddFalsePositiveTriageV1Analyzer,
)


def test_v134ew_commercial_aerospace_ev_add_false_positive_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EWCommercialAerospaceEVAddFalsePositiveTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "keep_add_positive_rules_seed_only_and_shift_next_to_context_gating_audit"
    )
    assert result.summary["non_seed_positive_hit_count"] == 495
