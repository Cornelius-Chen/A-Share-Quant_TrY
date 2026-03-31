from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.market_v6_q3_first_lane_acceptance import (
    MarketV6Q3FirstLaneAcceptanceAnalyzer,
    load_json_report,
    write_market_v6_q3_first_lane_acceptance_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Accept or reject the first v6 q3/C bounded lane.")
    parser.add_argument(
        "--config",
        default="config/market_v6_q3_first_lane_acceptance_v1.yaml",
        help="Path to the market v6 q3 first-lane acceptance YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = MarketV6Q3FirstLaneAcceptanceAnalyzer().analyze(
        divergence_payload=load_json_report(Path(config["paths"]["divergence_report"])),
        opening_payload=load_json_report(Path(config["paths"]["opening_report"])),
        persistence_payload=load_json_report(Path(config["paths"]["persistence_report"])),
    )
    output_path = write_market_v6_q3_first_lane_acceptance_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Market-v6 q3 first-lane acceptance report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
