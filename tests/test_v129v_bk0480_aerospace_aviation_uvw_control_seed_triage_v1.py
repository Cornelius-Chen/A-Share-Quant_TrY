from pathlib import Path

from a_share_quant.strategy.v129v_bk0480_aerospace_aviation_uvw_control_seed_triage_v1 import (
    V129VBK0480AerospaceAviationUVWControlSeedTriageAnalyzer,
)


def test_v129v_bk0480_aerospace_aviation_uvw_control_seed_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129VBK0480AerospaceAviationUVWControlSeedTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == (
        "freeze_bk0480_minimal_control_seed_and_move_to_control_seed_audit"
    )
    assert any(row["direction"] == "next_phase" for row in result.direction_rows)
