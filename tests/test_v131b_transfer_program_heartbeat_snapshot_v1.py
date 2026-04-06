from pathlib import Path

from a_share_quant.strategy.v131b_transfer_program_heartbeat_snapshot_v1 import (
    V131BTransferProgramHeartbeatSnapshotAnalyzer,
)


def test_v131b_transfer_program_heartbeat_snapshot_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131BTransferProgramHeartbeatSnapshotAnalyzer(repo_root).analyze()

    assert result.summary["program_status"] == "frozen"
    assert result.summary["rerun_required"] is False
    assert result.summary["nearest_candidate_sector_id"] == "BK0808"
    assert result.summary["decisive_watch_symbol"] == "600118"
    assert result.summary["authoritative_status"] == "heartbeat_snapshot_ready_for_daily_do_not_rerun_check"
