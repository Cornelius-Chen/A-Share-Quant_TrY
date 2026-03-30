from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.market_v4_q2_first_lane_acceptance import (
    MarketV4Q2FirstLaneAcceptanceAnalyzer,
    load_json_report,
    write_market_v4_q2_first_lane_acceptance_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Decide whether the first v4 q2 lane changes the current carry-row-diversity reading."
    )
    parser.add_argument(
        "--config",
        default="config/market_v4_q2_first_lane_acceptance_v1.yaml",
        help="Path to the v4 q2 first-lane acceptance YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = MarketV4Q2FirstLaneAcceptanceAnalyzer().analyze(
        divergence_payload=load_json_report(Path(config["paths"]["divergence_report"])),
        opening_payload=load_json_report(Path(config["paths"]["opening_report"])),
        persistence_payload=load_json_report(Path(config["paths"]["persistence_report"])),
    )
    output_path = write_market_v4_q2_first_lane_acceptance_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Market-v4 q2 first-lane acceptance report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
