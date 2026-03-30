from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_v4_hunt_phase_check_v1 import (
    V12V4HuntPhaseCheckAnalyzer,
    load_json_report,
    write_v12_v4_hunt_phase_check_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether the current v4 hunt should pause before lower-priority tracks.")
    parser.add_argument(
        "--config",
        default="config/v12_v4_hunt_phase_check_v1.yaml",
        help="Path to the v12 v4 hunt phase-check YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12V4HuntPhaseCheckAnalyzer().analyze(
        hunting_strategy_payload=load_json_report(Path(config["paths"]["hunting_strategy_report"])),
        bottleneck_check_payload=load_json_report(Path(config["paths"]["bottleneck_check_report"])),
        first_hunt_payload=load_json_report(Path(config["paths"]["first_hunt_report"])),
        second_hunt_payload=load_json_report(Path(config["paths"]["second_hunt_report"])),
        third_hunt_payload=load_json_report(Path(config["paths"]["third_hunt_report"])),
        fourth_hunt_payload=load_json_report(Path(config["paths"]["fourth_hunt_report"])),
    )
    output_path = write_v12_v4_hunt_phase_check_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.2 v4 hunt phase check: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
