from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_carry_row_hunting_strategy_v1 import (
    V12CarryRowHuntingStrategyAnalyzer,
    load_json_report,
    write_v12_carry_row_hunting_strategy_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze the next single-lane carry-row hunt order inside the existing v4 refresh."
    )
    parser.add_argument(
        "--config",
        default="config/v12_carry_row_hunting_strategy_v1.yaml",
        help="Path to the carry row hunting strategy YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12CarryRowHuntingStrategyAnalyzer().analyze(
        v4_manifest_payload=load_json_report(Path(config["paths"]["v4_manifest_report"])),
        v4_first_lane_payload=load_json_report(Path(config["paths"]["v4_first_lane_acceptance_report"])),
        training_manifest_payload=load_json_report(Path(config["paths"]["training_manifest_report"])),
    )
    output_path = write_v12_carry_row_hunting_strategy_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V12 carry row hunting strategy report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
