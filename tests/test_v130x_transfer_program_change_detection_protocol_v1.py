from pathlib import Path

from a_share_quant.strategy.v130x_transfer_program_change_detection_protocol_v1 import (
    V130XTransferProgramChangeDetectionProtocolAnalyzer,
)


def test_v130x_transfer_program_change_detection_protocol_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130XTransferProgramChangeDetectionProtocolAnalyzer(repo_root).analyze()

    assert result.summary["artifact_count"] == 5
    assert result.summary["authoritative_status"] == "transfer_program_frozen_until_monitored_artifacts_change"
    assert all(row["exists"] is True for row in result.artifact_rows)
