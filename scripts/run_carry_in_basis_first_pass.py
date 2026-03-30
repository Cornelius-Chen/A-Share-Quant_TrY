from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.carry_in_basis_first_pass import (
    CarryInBasisFirstPassAnalyzer,
    load_json_report,
    write_carry_in_basis_first_pass_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the first bounded carry-in-basis factor evaluation.")
    parser.add_argument(
        "--config",
        default="config/carry_in_basis_first_pass_v1.yaml",
        help="Path to the carry-in-basis first-pass YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = CarryInBasisFirstPassAnalyzer().analyze(
        protocol_payload=load_json_report(ROOT / config["inputs"]["protocol_report"]),
        family_inventory_payload=load_json_report(ROOT / config["inputs"]["family_inventory_report"]),
        cross_strategy_payload=load_json_report(ROOT / config["inputs"]["cross_strategy_report"]),
        mechanism_b_payload=load_json_report(ROOT / config["inputs"]["mechanism_b_report"]),
        mechanism_c_payload=load_json_report(ROOT / config["inputs"]["mechanism_c_report"]),
    )
    output_path = write_carry_in_basis_first_pass_report(
        reports_dir=ROOT / config["paths"]["reports_dir"],
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Carry-in-basis first-pass report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
