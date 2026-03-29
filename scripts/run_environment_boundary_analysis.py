from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.environment_boundary import (
    EnvironmentBoundaryAnalyzer,
    load_validation_report,
    write_environment_boundary_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze environment boundaries from a time-slice validation report.")
    parser.add_argument(
        "--config",
        default="config/environment_boundary_analysis.yaml",
        help="Path to the environment-boundary analysis YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)
    validation_report_path = Path(config["paths"]["validation_report"])
    payload = load_validation_report(validation_report_path)
    payload["source_report"] = str(validation_report_path)
    result = EnvironmentBoundaryAnalyzer().analyze(payload)
    report_path = write_environment_boundary_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Environment boundary report: {report_path}")
    print(f"Boundary summary: {result.boundary_summary}")


if __name__ == "__main__":
    main()
