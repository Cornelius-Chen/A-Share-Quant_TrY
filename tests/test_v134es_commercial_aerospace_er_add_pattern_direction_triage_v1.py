from pathlib import Path

from a_share_quant.strategy.v134es_commercial_aerospace_er_add_pattern_direction_triage_v1 import (
    V134ESCommercialAerospaceERAddPatternDirectionTriageV1Analyzer,
)


def test_v134es_commercial_aerospace_er_add_pattern_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ESCommercialAerospaceERAddPatternDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "freeze_local_add_pattern_envelopes_and_shift_next_to_add_rule_candidate_audit"
    )
    assert result.summary["label_tier_count"] == 4
