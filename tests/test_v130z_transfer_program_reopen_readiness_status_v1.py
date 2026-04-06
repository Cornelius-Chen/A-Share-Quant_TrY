from pathlib import Path

from a_share_quant.strategy.v130z_transfer_program_reopen_readiness_status_v1 import (
    V130ZTransferProgramReopenReadinessStatusAnalyzer,
)


def test_v130z_transfer_program_reopen_readiness_status_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130ZTransferProgramReopenReadinessStatusAnalyzer(repo_root).analyze()

    assert result.summary["artifact_count"] == 5
    assert result.summary["changed_artifact_count"] == 0
    assert result.summary["missing_artifact_count"] == 0
    assert result.summary["rerun_required"] is False
    assert result.summary["authoritative_status"] == "no_rerun_required_under_current_static_artifacts"
