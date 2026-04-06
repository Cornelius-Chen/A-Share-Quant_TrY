from pathlib import Path

from a_share_quant.strategy.v129r_bk0480_aerospace_aviation_transfer_worker_kickoff_triage_v1 import (
    V129RBK0480AerospaceAviationTransferWorkerKickoffTriageAnalyzer,
)


def test_v129r_bk0480_aerospace_aviation_transfer_worker_kickoff_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129RBK0480AerospaceAviationTransferWorkerKickoffTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == (
        "bk0480_transfer_worker_started_from_dual_core_world_model_with_local_reset"
    )
    assert any(row["direction"] == "next_phase" for row in result.direction_rows)
