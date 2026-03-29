from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.cross_strategy_cycle_consistency_analysis import (
    CrossStrategyCycleConsistencyAnalyzer,
    load_json_report,
    write_cross_strategy_cycle_consistency_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare drawdown-cycle mechanisms across strategies.")
    parser.add_argument(
        "--config",
        default="config/baseline_q3_cross_strategy_cycle_consistency_v1.yaml",
        help="Path to the cross-strategy cycle consistency YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    payloads = [load_json_report(Path(path)) for path in config["paths"]["mechanism_reports"]]
    result = CrossStrategyCycleConsistencyAnalyzer().analyze(report_payloads=payloads)
    output_path = write_cross_strategy_cycle_consistency_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Cross-strategy cycle consistency report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
