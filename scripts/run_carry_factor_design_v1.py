from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.carry_factor_design_v1 import (
    CarryFactorDesignAnalyzer,
    load_json_report,
    write_carry_factor_design_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Design the first bounded carry factor lane.")
    parser.add_argument(
        "--config",
        default="config/carry_factor_design_v1.yaml",
        help="Path to the carry factor design YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = CarryFactorDesignAnalyzer().analyze(
        first_pass_payload=load_json_report(ROOT / config["inputs"]["first_pass_report"]),
        mechanism_b_payload=load_json_report(ROOT / config["inputs"]["mechanism_b_report"]),
        mechanism_c_payload=load_json_report(ROOT / config["inputs"]["mechanism_c_report"]),
        cross_strategy_payload=load_json_report(ROOT / config["inputs"]["cross_strategy_report"]),
    )
    output_path = write_carry_factor_design_report(
        reports_dir=ROOT / config["paths"]["reports_dir"],
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Carry factor design report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
