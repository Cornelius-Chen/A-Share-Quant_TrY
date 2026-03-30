from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_training_readiness_check_v1 import (
    V12TrainingReadinessCheckAnalyzer,
    load_json_report,
    write_v12_training_readiness_check_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether the current bounded training pilot is ready to expand."
    )
    parser.add_argument(
        "--config",
        default="config/v12_training_readiness_check_v1.yaml",
        help="Path to the training-readiness check YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12TrainingReadinessCheckAnalyzer().analyze(
        pilot_payload=load_json_report(Path(config["paths"]["pilot_report"])),
    )
    output_path = write_v12_training_readiness_check_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V12 training readiness check report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
