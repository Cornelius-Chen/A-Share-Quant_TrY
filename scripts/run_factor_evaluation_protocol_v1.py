from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.factor_evaluation_protocol_v1 import (
    FactorEvaluationProtocolAnalyzer,
    load_json_report,
    write_factor_evaluation_protocol_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the first factor evaluation protocol.")
    parser.add_argument(
        "--config",
        default="config/factor_evaluation_protocol_v1.yaml",
        help="Path to the factor evaluation protocol YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = FactorEvaluationProtocolAnalyzer().analyze(
        registry_payload=load_json_report(ROOT / config["inputs"]["registry_report"]),
        family_inventory_payload=load_json_report(ROOT / config["inputs"]["family_inventory_report"]),
    )
    output_path = write_factor_evaluation_protocol_report(
        reports_dir=ROOT / config["paths"]["reports_dir"],
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Factor evaluation protocol report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
