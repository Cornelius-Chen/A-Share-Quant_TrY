from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112az_cpo_bounded_training_layer_extension_v1 import (
    V112AZCPOBoundedTrainingLayerExtensionAnalyzer,
    load_json_report,
    write_v112az_cpo_bounded_training_layer_extension_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AZ bounded training layer extension.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112AZCPOBoundedTrainingLayerExtensionAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        dataset_assembly_payload=load_json_report(Path(config["paths"]["v112aj_dataset_report"])),
        branch_training_layer_review_payload=load_json_report(Path(config["paths"]["v112ay_training_layer_review_report"])),
    )
    output_path = write_v112az_cpo_bounded_training_layer_extension_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AZ bounded training layer extension report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
