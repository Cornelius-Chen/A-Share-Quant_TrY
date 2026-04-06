from pathlib import Path

from a_share_quant.strategy.v129m_commercial_aerospace_klm_governance_packaging_triage_v1 import (
    V129MCommercialAerospaceKLMGovernancePackagingTriageAnalyzer,
)


def test_v129m_commercial_aerospace_klm_governance_packaging_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129MCommercialAerospaceKLMGovernancePackagingTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == (
        "freeze_commercial_aerospace_primary_plus_governance_and_shift_to_transfer_preparation"
    )
    assert len(result.direction_rows) == 4
