from pathlib import Path

from a_share_quant.strategy.v133l_program_master_heartbeat_snapshot_v1 import (
    V133LProgramMasterHeartbeatSnapshotAnalyzer,
)


def test_v133l_program_master_heartbeat_snapshot_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133LProgramMasterHeartbeatSnapshotAnalyzer(repo_root).analyze()

    assert report.summary["program_status"] == "frozen"
    assert report.summary["frozen_line_count"] == 5
