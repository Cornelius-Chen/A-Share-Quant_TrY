from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pg_a_share_tushare_limit_halt_semantic_side_inputs_bootstrap_v1 import main


def test_v134pg_semantic_side_inputs_bootstrap_outputs_exist() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    main()

    assert (
        repo_root / "reports" / "analysis" / "v134pg_a_share_tushare_limit_halt_semantic_side_inputs_bootstrap_v1.json"
    ).exists()
    assert (repo_root / "data" / "reference" / "namechange" / "tushare_commercial_aerospace_namechange_v1.csv").exists()
    assert (repo_root / "data" / "reference" / "suspend_d" / "tushare_commercial_aerospace_suspend_d_v1.csv").exists()
