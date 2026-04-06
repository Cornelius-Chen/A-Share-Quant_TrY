from pathlib import Path

from a_share_quant.strategy.v130o_bk0808_military_civil_fusion_no_worker_watch_triage_v1 import (
    V130OBK0808MilitaryCivilFusionNoWorkerWatchTriageAnalyzer,
)


def test_v130o_bk0808_military_civil_fusion_no_worker_watch_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130OBK0808MilitaryCivilFusionNoWorkerWatchTriageAnalyzer(repo_root).analyze()

    assert result.summary["nearest_same_plane_watch"] == ["600118"]
    assert result.summary["authoritative_status"] == "monitor_bk0808_emergence_candidates_without_unlocking_a_worker"
    assert any(
        row["symbol"] == "600118" and row["direction"] == "watch_as_second_same_plane_candidate_but_do_not_open_worker"
        for row in result.triage_rows
    )
