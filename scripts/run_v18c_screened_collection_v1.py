from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v18c_screened_collection_v1 import (
    V18CScreenedCollectionAnalyzer,
    load_json_report,
    write_v18c_screened_collection_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V1.8C screened bounded collection.")
    parser.add_argument(
        "--config",
        default="config/v18c_screened_collection_v1.yaml",
        help="Path to the V1.8C screened collection config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V18CScreenedCollectionAnalyzer().analyze(
        screened_collection_protocol_payload=load_json_report(
            Path(config["paths"]["v18c_screened_collection_protocol_report"])
        ),
        catalyst_seed_payload=load_json_report(Path(config["paths"]["catalyst_seed_report"])),
        market_v5_first_lane_payload=load_json_report(Path(config["paths"]["market_v5_first_lane_acceptance_report"])),
        market_v5_last_probe_payload=load_json_report(
            Path(config["paths"]["market_v5_last_probe_acceptance_report"])
        ),
        market_v6_first_lane_payload=load_json_report(Path(config["paths"]["market_v6_first_lane_acceptance_report"])),
    )
    output_path = write_v18c_screened_collection_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.8C screened collection report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
