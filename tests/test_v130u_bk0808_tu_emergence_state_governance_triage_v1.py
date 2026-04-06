from pathlib import Path

from a_share_quant.strategy.v130u_bk0808_tu_emergence_state_governance_triage_v1 import (
    V130UBK0808TUEmergenceStateGovernanceTriageAnalyzer,
)


def test_v130u_bk0808_tu_emergence_state_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130UBK0808TUEmergenceStateGovernanceTriageAnalyzer(repo_root).analyze()

    assert result.summary["symbol"] == "600118"
    assert result.state_counts["near_surface_watch"] > 0
    assert result.summary["authoritative_status"] == "retain_bk0808_watch_state_machine_as_governance_only_and_keep_worker_frozen"
