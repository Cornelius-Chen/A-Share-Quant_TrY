from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.market_v5_q2_last_carry_probe_acceptance import (
    MarketV5Q2LastCarryProbeAcceptanceAnalyzer,
    load_json_report,
    write_market_v5_q2_last_carry_probe_acceptance_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Close the last bounded v5 true-carry probe.")
    parser.add_argument(
        "--config",
        default="config/market_v5_q2_last_carry_probe_acceptance_000099_v1.yaml",
        help="Path to the v5 q2 last-carry-probe acceptance YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = MarketV5Q2LastCarryProbeAcceptanceAnalyzer().analyze(
        target_symbol=str(config["analysis"]["target_symbol"]),
        reassessment_payload=load_json_report(Path(config["paths"]["reassessment_report"])),
        divergence_payload=load_json_report(Path(config["paths"]["divergence_report"])),
        opening_payload=load_json_report(Path(config["paths"]["opening_report"])),
        persistence_payload=load_json_report(Path(config["paths"]["persistence_report"])),
    )
    output_path = write_market_v5_q2_last_carry_probe_acceptance_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Market-v5 q2 last-carry-probe acceptance report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
