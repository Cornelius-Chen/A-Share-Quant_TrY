from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.market_q2_capture_slice_acceptance import (
    MarketQ2CaptureSliceAcceptanceAnalyzer,
    load_json_report,
    write_market_q2_capture_slice_acceptance_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decide whether the market-v1 q2 capture slice should continue replay.")
    parser.add_argument(
        "--config",
        default="config/market_v1_q2_capture_slice_acceptance_v1.yaml",
        help="Path to the q2 capture slice acceptance YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = MarketQ2CaptureSliceAcceptanceAnalyzer().analyze(
        divergence_payload=load_json_report(Path(config["paths"]["divergence_report"])),
        persistence_payload=load_json_report(Path(config["paths"]["persistence_report"])),
        opening_payload=load_json_report(Path(config["paths"]["opening_report"])),
    )
    output_path = write_market_q2_capture_slice_acceptance_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Market q2 capture slice acceptance report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
