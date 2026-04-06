from pathlib import Path

from a_share_quant.strategy.v131l_commercial_aerospace_intraday_collection_governance_triage_v1 import (
    V131LCommercialAerospaceIntradayCollectionGovernanceTriageAnalyzer,
)


def test_v131l_commercial_aerospace_intraday_collection_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131LCommercialAerospaceIntradayCollectionGovernanceTriageAnalyzer(repo_root).analyze()

    assert result.summary["required_artifact_count"] == 4
    assert result.summary["missing_artifact_count"] == 4
    assert (
        result.summary["authoritative_status"]
        == "freeze_intraday_collection_governance_until_required_minute_files_arrive"
    )
