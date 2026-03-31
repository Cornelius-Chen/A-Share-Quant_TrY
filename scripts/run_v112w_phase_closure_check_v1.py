from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112w_phase_closure_check_v1 import (
    V112WPhaseClosureCheckAnalyzer,
    load_json_report,
    write_v112w_phase_closure_check_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12W phase closure check.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112WPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path(config["paths"]["v112w_phase_check_report"]))
    )
    output_path = write_v112w_phase_closure_check_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12W phase closure report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
