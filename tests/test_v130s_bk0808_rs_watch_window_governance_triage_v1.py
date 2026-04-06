from pathlib import Path

from a_share_quant.strategy.v130s_bk0808_rs_watch_window_governance_triage_v1 import (
    V130SBK0808RSWatchWindowGovernanceTriageAnalyzer,
)


def test_v130s_bk0808_rs_watch_window_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130SBK0808RSWatchWindowGovernanceTriageAnalyzer(repo_root).analyze()

    assert result.summary["near_surface_watch_day_count"] > 0
    assert result.summary["authoritative_status"] == "retain_bk0808_watch_windows_for_governance_but_keep_worker_frozen"
