from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112bq_phase_check_v1 import (
    V112BQPhaseCheckAnalyzer,
    load_json_report,
    write_v112bq_phase_check_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BQ phase check.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112BQPhaseCheckAnalyzer()
    result = analyzer.analyze(gate_precision_payload=load_json_report(Path(config["paths"]["gate_precision_report"])))
    output_path = write_v112bq_phase_check_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BQ phase check report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()

