from pathlib import Path

from a_share_quant.strategy.v131i_commercial_aerospace_intraday_data_governance_triage_v1 import (
    V131ICommercialAerospaceIntradayDataGovernanceTriageAnalyzer,
)


def test_v131i_commercial_aerospace_intraday_data_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131ICommercialAerospaceIntradayDataGovernanceTriageAnalyzer(repo_root).analyze()

    assert result.summary["missing_required_symbol_count"] == 4
    assert result.summary["manifest_row_count"] == 4
    assert (
        result.summary["authoritative_status"]
        == "keep_intraday_override_governance_bundle_but_block_intraday_modeling_until_minute_data_arrives"
    )
