from pathlib import Path

from a_share_quant.strategy.v129x_bk0480_aerospace_aviation_wx_control_seed_triage_v1 import (
    V129XBK0480AerospaceAviationWXControlSeedTriageAnalyzer,
)


def test_v129x_bk0480_aerospace_aviation_wx_control_seed_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129XBK0480AerospaceAviationWXControlSeedTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == (
        "retain_bk0480_dual_core_seed_but_block_replay_and_move_to_local_universe_expansion"
    )
    assert any(row["direction"] == "bk0480_local_universe_expansion" for row in result.direction_rows)
