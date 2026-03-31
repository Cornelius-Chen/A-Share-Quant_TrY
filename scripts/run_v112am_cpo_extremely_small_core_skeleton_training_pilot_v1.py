from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
    load_json_report,
    write_v112am_cpo_extremely_small_core_skeleton_training_pilot_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AM core-skeleton training pilot.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112am_phase_charter_report"])),
        readiness_review_payload=load_json_report(Path(config["paths"]["v112al_readiness_review_report"])),
        dataset_assembly_payload=load_json_report(Path(config["paths"]["v112aj_dataset_report"])),
        cycle_reconstruction_payload=load_json_report(Path(config["paths"]["v112z_cycle_reconstruction_report"])),
    )
    output_path = write_v112am_cpo_extremely_small_core_skeleton_training_pilot_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AM training pilot report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
