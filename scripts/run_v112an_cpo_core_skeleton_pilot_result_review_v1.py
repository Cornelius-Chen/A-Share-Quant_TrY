from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112an_cpo_core_skeleton_pilot_result_review_v1 import (
    V112ANCPOCoreSkeletonPilotResultReviewAnalyzer,
    load_json_report,
    write_v112an_cpo_core_skeleton_pilot_result_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AN core-skeleton pilot result review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112ANCPOCoreSkeletonPilotResultReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112an_phase_charter_report"])),
        training_pilot_payload=load_json_report(Path(config["paths"]["v112am_training_pilot_report"])),
        dataset_assembly_payload=load_json_report(Path(config["paths"]["v112aj_dataset_report"])),
        cycle_reconstruction_payload=load_json_report(Path(config["paths"]["v112z_cycle_reconstruction_report"])),
    )
    output_path = write_v112an_cpo_core_skeleton_pilot_result_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AN result review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
