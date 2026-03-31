from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112b_baseline_readout_v1 import (
    V112BBaselineReadoutAnalyzer,
    load_json_report,
    write_v112b_baseline_readout_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12B baseline readout.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112BBaselineReadoutAnalyzer()
    result = analyzer.analyze(
        pilot_dataset_payload=load_json_report(Path(config["paths"]["v112b_pilot_dataset_freeze_report"])),
        training_protocol_payload=load_json_report(Path(config["paths"]["v112_training_protocol_report"])),
    )
    output_path = write_v112b_baseline_readout_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12B baseline readout report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
