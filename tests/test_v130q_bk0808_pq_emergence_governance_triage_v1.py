from pathlib import Path

from a_share_quant.strategy.v130q_bk0808_pq_emergence_governance_triage_v1 import (
    V130QBK0808PQEmergenceGovernanceTriageAnalyzer,
)


def test_v130q_bk0808_pq_emergence_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130QBK0808PQEmergenceGovernanceTriageAnalyzer(repo_root).analyze()

    assert result.summary["reopen_candidate_symbol"] == "600118"
    assert result.summary["authoritative_status"] == "monitor_600118_as_bk0808_emergence_trigger_but_keep_worker_frozen_until_real_same_plane_support_appears"
    assert any(row["symbol"] == "600118" and row["direction"] == "reopen_candidate_only_after_real_v6_emergence" for row in result.triage_rows)
