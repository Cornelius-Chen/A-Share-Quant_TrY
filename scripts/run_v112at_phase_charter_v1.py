from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112at_phase_charter_v1 import (
    V112ATPhaseCharterAnalyzer,
    load_json_report,
    write_v112at_phase_charter_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AT phase charter.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112ATPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112as_phase_closure_payload=load_json_report(Path(config["paths"]["v112as_phase_closure_report"])),
    )
    output_path = write_v112at_phase_charter_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AT phase charter report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
