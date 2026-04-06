from pathlib import Path

from a_share_quant.strategy.v128q_commercial_aerospace_opq_timechain_governance_triage_v1 import (
    V128QCommercialAerospaceOPQTimechainGovernanceTriageAnalyzer,
)


def test_v128q_commercial_aerospace_opq_timechain_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128QCommercialAerospaceOPQTimechainGovernanceTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"].startswith("retain_time_chain_triplet")
    assert any(row["theme"] == "preopen_decisive_event_veto" for row in result.retained_rows)
