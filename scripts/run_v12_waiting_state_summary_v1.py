from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_waiting_state_summary_v1 import (
    V12WaitingStateSummaryAnalyzer,
    load_json_report,
    write_v12_waiting_state_summary_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V1.2 waiting-state summary.")
    parser.add_argument(
        "--config",
        default="config/v12_waiting_state_summary_v1.yaml",
        help="Path to the V1.2 waiting-state summary config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12WaitingStateSummaryAnalyzer().analyze(
        bottleneck_check_payload=load_json_report(Path(config["paths"]["bottleneck_check_report"])),
        v6_first_lane_phase_check_payload=load_json_report(Path(config["paths"]["v6_first_lane_phase_check_report"])),
        v6_reassessment_payload=load_json_report(Path(config["paths"]["v6_reassessment_report"])),
    )
    output_path = write_v12_waiting_state_summary_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.2 waiting-state summary report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
