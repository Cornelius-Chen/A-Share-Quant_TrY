from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113h_phase_charter_v1 import (
    V113HPhaseCharterAnalyzer,
    load_json_report,
    write_v113h_phase_charter_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13H phase charter.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V113HPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112cw_payload=load_json_report(Path(config["paths"]["v112cw_report"])),
        v112cx_payload=load_json_report(Path(config["paths"]["v112cx_report"])),
        owner_approves_execution_transition=bool(config["inputs"]["owner_approves_execution_transition"]),
    )
    output_path = write_v113h_phase_charter_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13H phase charter report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
