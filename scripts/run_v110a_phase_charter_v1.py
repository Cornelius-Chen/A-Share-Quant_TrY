from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v110a_phase_charter_v1 import (
    V110APhaseCharterAnalyzer,
    load_json_report,
    write_v110a_phase_charter_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.10A phase charter.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V110APhaseCharterAnalyzer()
    result = analyzer.analyze(
        v19_phase_closure_payload=load_json_report(Path(config["paths"]["v19_phase_closure_report"])),
        v19_feature_breadth_rereview_payload=load_json_report(Path(config["paths"]["v19_feature_breadth_rereview_report"])),
    )
    output_path = write_v110a_phase_charter_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.10A phase charter report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
