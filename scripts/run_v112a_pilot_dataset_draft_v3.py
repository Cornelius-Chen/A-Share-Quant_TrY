from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112a_pilot_dataset_draft_v3 import (
    V112APilotDatasetDraftV3Analyzer,
    load_json_report,
    write_v112a_pilot_dataset_draft_v3_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12A pilot dataset draft v3.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112APilotDatasetDraftV3Analyzer()
    result = analyzer.analyze(
        pilot_dataset_draft_v1_payload=load_json_report(Path(config["paths"]["v112a_pilot_dataset_draft_v1_report"])),
        price_cycle_inference_v2_payload=load_json_report(Path(config["paths"]["v112a_price_cycle_inference_v2_report"])),
    )
    output_path = write_v112a_pilot_dataset_draft_v3_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12A pilot dataset draft v3 report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
