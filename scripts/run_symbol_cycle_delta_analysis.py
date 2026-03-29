from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.symbol_cycle_delta_analysis import (
    SymbolCycleDeltaAnalyzer,
    load_timeline_report,
    write_symbol_cycle_delta_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare exact trade cycles between incumbent and challenger for one symbol.")
    parser.add_argument(
        "--config",
        default="config/baseline_q3_symbol_cycle_delta_600519_v1.yaml",
        help="Path to the symbol cycle-delta YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    payload = load_timeline_report(Path(config["paths"]["timeline_report"]))
    result = SymbolCycleDeltaAnalyzer().analyze(
        payload=payload,
        strategy_name=str(config["analysis"]["strategy_name"]),
        incumbent_name=str(config["analysis"]["incumbent_candidate"]),
        challenger_name=str(config["analysis"]["challenger_candidate"]),
    )
    output_path = write_symbol_cycle_delta_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Symbol cycle delta report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
