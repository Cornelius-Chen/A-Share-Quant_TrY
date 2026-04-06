from pathlib import Path

from a_share_quant.strategy.v134df_commercial_aerospace_intraday_add_prelaunch_heartbeat_v1 import (
    V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Analyzer,
    write_report as write_heartbeat_report,
)
from a_share_quant.strategy.v134dg_commercial_aerospace_df_prelaunch_playbook_v1 import (
    V134DGCommercialAerospaceDFPrelaunchPlaybookV1Analyzer,
)


def test_v134dg_commercial_aerospace_df_prelaunch_playbook_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    heartbeat = V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Analyzer(repo_root).analyze()
    write_heartbeat_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134df_commercial_aerospace_intraday_add_prelaunch_heartbeat_v1",
        result=heartbeat,
    )
    result = V134DGCommercialAerospaceDFPrelaunchPlaybookV1Analyzer(repo_root).analyze()

    assert result.summary["frontier_state"] == "deferred"
    assert result.summary["opening_gate_count"] == 9
    assert result.summary["playbook_step_count"] == 5
