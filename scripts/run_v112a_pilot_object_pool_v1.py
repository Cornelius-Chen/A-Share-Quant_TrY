from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112a_pilot_object_pool_v1 import (
    V112APilotObjectPoolAnalyzer,
    load_json_report,
    write_v112a_pilot_object_pool_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12A pilot object pool.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112APilotObjectPoolAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112a_phase_charter_report"])),
    )
    output_path = write_v112a_pilot_object_pool_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12A pilot object pool report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
