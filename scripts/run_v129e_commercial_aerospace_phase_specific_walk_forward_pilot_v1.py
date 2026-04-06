from pathlib import Path

from a_share_quant.strategy.v129e_commercial_aerospace_phase_specific_walk_forward_pilot_v1 import (
    V129ECommercialAerospacePhaseSpecificWalkForwardPilotAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129ECommercialAerospacePhaseSpecificWalkForwardPilotAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129e_commercial_aerospace_phase_specific_walk_forward_pilot_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
