from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.drawdown_gap_analysis import (
    DrawdownGapAnalyzer,
    load_validation_report,
    write_drawdown_gap_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze remaining drawdown gap from a time-slice report.")
    parser.add_argument(
        "--config",
        default="config/buffer_only_012_drawdown_gap_analysis_v1.yaml",
        help="Path to the drawdown-gap analysis YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)
    report_path = Path(config["paths"]["comparison_report"])
    payload = load_validation_report(report_path)
    result = DrawdownGapAnalyzer().analyze(
        payload=payload,
        incumbent_name=str(config["analysis"]["incumbent_candidate"]),
        challenger_name=str(config["analysis"]["challenger_candidate"]),
    )
    output_path = write_drawdown_gap_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Drawdown gap report: {output_path}")
    print(f"Summary: {result.summary}")
    weakest_dataset_strategy = result.summary.get("weakest_dataset_strategy")
    if weakest_dataset_strategy is not None:
        print(f"Weakest dataset-strategy: {weakest_dataset_strategy}")


if __name__ == "__main__":
    main()
