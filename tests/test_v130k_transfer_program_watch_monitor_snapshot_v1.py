from pathlib import Path

from a_share_quant.strategy.v130k_transfer_program_watch_monitor_snapshot_v1 import (
    V130KTransferProgramWatchMonitorSnapshotAnalyzer,
)


def test_v130k_transfer_program_watch_monitor_snapshot_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130KTransferProgramWatchMonitorSnapshotAnalyzer(repo_root).analyze()

    assert result.summary["reopen_ready_count"] == 0
    assert result.summary["closest_candidate_sector_id"] == "BK0808"
    assert result.summary["authoritative_status"] == "freeze_transfer_program_and_monitor_gap_closure"
    assert result.monitor_rows[0]["sector_id"] == "BK0808"
