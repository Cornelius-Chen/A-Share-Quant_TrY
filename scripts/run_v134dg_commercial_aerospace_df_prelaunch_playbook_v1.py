from pathlib import Path

from a_share_quant.strategy.v134df_commercial_aerospace_intraday_add_prelaunch_heartbeat_v1 import (
    V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Analyzer,
    write_report as write_heartbeat_report,
)
from a_share_quant.strategy.v134dg_commercial_aerospace_df_prelaunch_playbook_v1 import (
    V134DGCommercialAerospaceDFPrelaunchPlaybookV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    heartbeat = V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Analyzer(repo_root).analyze()
    write_heartbeat_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134df_commercial_aerospace_intraday_add_prelaunch_heartbeat_v1",
        result=heartbeat,
    )
    result = V134DGCommercialAerospaceDFPrelaunchPlaybookV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134dg_commercial_aerospace_df_prelaunch_playbook_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
