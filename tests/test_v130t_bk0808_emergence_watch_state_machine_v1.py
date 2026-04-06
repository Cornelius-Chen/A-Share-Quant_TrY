from pathlib import Path

from a_share_quant.strategy.v130t_bk0808_emergence_watch_state_machine_v1 import (
    V130TBK0808EmergenceWatchStateMachineAnalyzer,
)


def test_v130t_bk0808_emergence_watch_state_machine_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130TBK0808EmergenceWatchStateMachineAnalyzer(repo_root).analyze()

    assert result.summary["symbol"] == "600118"
    assert result.summary["near_surface_watch_day_count"] > 0
    assert result.summary["current_reopen_candidate_state"] is False
    assert result.summary["authoritative_status"] == "bk0808_watch_state_machine_operational_but_worker_still_frozen"
