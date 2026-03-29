from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.symbol_path_shift_analysis import (
    SymbolPathShiftAnalyzer,
    load_timeline_report,
    write_symbol_path_shift_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze incumbent/challenger daily path shifts for one symbol timeline.")
    parser.add_argument(
        "--config",
        default="config/theme_q1_symbol_path_shift_300750_v1.yaml",
        help="Path to the symbol path-shift YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)
    payload = load_timeline_report(Path(config["paths"]["timeline_report"]))
    result = SymbolPathShiftAnalyzer().analyze(
        payload=payload,
        incumbent_name=str(config["analysis"]["incumbent_candidate"]),
        challenger_name=str(config["analysis"]["challenger_candidate"]),
    )
    output_path = write_symbol_path_shift_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Symbol path-shift report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
