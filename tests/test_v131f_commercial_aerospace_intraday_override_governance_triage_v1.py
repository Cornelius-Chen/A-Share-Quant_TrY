from pathlib import Path

from a_share_quant.strategy.v131f_commercial_aerospace_intraday_override_governance_triage_v1 import (
    V131FCommercialAerospaceIntradayOverrideGovernanceTriageAnalyzer,
)


def test_v131f_commercial_aerospace_intraday_override_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131FCommercialAerospaceIntradayOverrideGovernanceTriageAnalyzer(repo_root).analyze()

    assert result.summary["override_positive_count"] == 2
    assert (
        result.summary["authoritative_status"]
        == "retain_intraday_override_supervision_bundle_and_keep_it_outside_current_lawful_replay"
    )
    assert any(row["component"] == "future_intraday_work" for row in result.triage_rows)
