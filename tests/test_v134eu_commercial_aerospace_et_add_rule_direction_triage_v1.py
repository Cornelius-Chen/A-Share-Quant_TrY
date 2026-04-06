from pathlib import Path

from a_share_quant.strategy.v134eu_commercial_aerospace_et_add_rule_direction_triage_v1 import (
    V134EUCommercialAerospaceETAddRuleDirectionTriageV1Analyzer,
)


def test_v134eu_commercial_aerospace_et_add_rule_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EUCommercialAerospaceETAddRuleDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_local_add_rule_candidates_as_governed_seed_rules_and_shift_next_to_broader_add_false_positive_audit"
    )
    assert result.summary["matched_count"] == result.summary["registry_row_count"]
