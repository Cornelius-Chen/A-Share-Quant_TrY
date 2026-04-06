from pathlib import Path

from a_share_quant.strategy.v132h_commercial_aerospace_gh_local_1min_rule_triage_v1 import (
    V132HCommercialAerospaceGHLocal1MinRuleTriageAnalyzer,
)


def test_v132h_local_1min_rule_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132HCommercialAerospaceGHLocal1MinRuleTriageAnalyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_local_1min_tier_rule_candidates_as_governed_seed_rules_and_shift_next_to_broader_false_positive_audit"
    )
    assert result.summary["matched_count"] == 6
