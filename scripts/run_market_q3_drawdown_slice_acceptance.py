from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.market_q3_drawdown_slice_acceptance import (
    MarketQ3DrawdownSliceAcceptanceAnalyzer,
    load_json_report,
    write_market_q3_drawdown_slice_acceptance_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decide whether market-v1 q3 drawdown slice needs more replay.")
    parser.add_argument(
        "--config",
        default="config/market_v1_q3_drawdown_slice_acceptance_v1.yaml",
        help="Path to the market-v1 q3 drawdown slice acceptance YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    divergence_payloads = [load_json_report(Path(path)) for path in config["paths"]["divergence_reports"]]
    consistency_payload = load_json_report(Path(config["paths"]["consistency_report"]))
    result = MarketQ3DrawdownSliceAcceptanceAnalyzer().analyze(
        divergence_payloads=divergence_payloads,
        consistency_payload=consistency_payload,
    )
    output_path = write_market_q3_drawdown_slice_acceptance_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Market q3 drawdown slice acceptance report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
