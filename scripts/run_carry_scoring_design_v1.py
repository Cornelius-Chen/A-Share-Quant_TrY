from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.carry_scoring_design_v1 import (
    CarryScoringDesignAnalyzer,
    load_json_report,
    write_carry_scoring_design_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run carry scoring design v1.")
    parser.add_argument(
        "--config",
        default="config/carry_scoring_design_v1.yaml",
        help="Path to the carry scoring design YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = CarryScoringDesignAnalyzer().analyze(
        schema_payload=load_json_report(ROOT / config["inputs"]["schema_report"]),
    )
    output_path = write_carry_scoring_design_report(
        reports_dir=ROOT / config["paths"]["reports_dir"],
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Carry scoring design report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
