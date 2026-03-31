from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112z_bounded_cycle_reconstruction_pass_v1 import (
    V112ZBoundedCycleReconstructionPassAnalyzer,
    load_json_report,
    write_v112z_bounded_cycle_reconstruction_pass_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12Z bounded cycle reconstruction pass.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112ZBoundedCycleReconstructionPassAnalyzer()
    result = analyzer.analyze(
        operational_charter_payload=load_json_report(Path(config["paths"]["v112z_operational_charter_report"])),
        protocol_payload=load_json_report(Path(config["paths"]["v112z_protocol_report"])),
        registry_schema_payload=load_json_report(Path(config["paths"]["v112q_registry_schema_report"])),
        pilot_dataset_payload=load_json_report(Path(config["paths"]["v112b_pilot_dataset_freeze_report"])),
        adjacent_validation_payload=load_json_report(Path(config["paths"]["v112r_adjacent_validation_report"])),
        chronology_payload=load_json_report(Path(config["paths"]["v112s_chronology_report"])),
        daily_board_payload=load_json_report(Path(config["paths"]["v112v_daily_board_report"])),
        future_calendar_payload=load_json_report(Path(config["paths"]["v112w_future_calendar_report"])),
        spillover_truth_payload=load_json_report(Path(config["paths"]["v112t_spillover_truth_report"])),
        spillover_factor_payload=load_json_report(Path(config["paths"]["v112x_spillover_factor_report"])),
        adjacent_split_payload=load_json_report(Path(config["paths"]["v112y_adjacent_split_report"])),
    )
    output_path = write_v112z_bounded_cycle_reconstruction_pass_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12Z bounded cycle reconstruction pass report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
