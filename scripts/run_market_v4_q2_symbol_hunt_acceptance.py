from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.market_v4_q2_symbol_hunt_acceptance import (
    MarketV4Q2SymbolHuntAcceptanceAnalyzer,
    load_json_report,
    write_market_v4_q2_symbol_hunt_acceptance_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Close or continue one v4 single-symbol hunt.")
    parser.add_argument(
        "--config",
        default="config/market_v4_q2_symbol_hunt_acceptance_000725_v1.yaml",
        help="Path to the symbol-hunt acceptance YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = MarketV4Q2SymbolHuntAcceptanceAnalyzer().analyze(
        target_symbol=str(config["analysis"]["target_symbol"]),
        excluded_symbols=[str(item) for item in config["analysis"].get("excluded_symbols", [])],
        hunting_strategy_payload=load_json_report(Path(config["paths"]["hunting_strategy_report"])),
        divergence_payload=load_json_report(Path(config["paths"]["divergence_report"])),
        opening_payload=load_json_report(Path(config["paths"]["opening_report"])),
        persistence_payload=load_json_report(Path(config["paths"]["persistence_report"])),
    )
    output_path = write_market_v4_q2_symbol_hunt_acceptance_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V4 q2 symbol-hunt acceptance: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
