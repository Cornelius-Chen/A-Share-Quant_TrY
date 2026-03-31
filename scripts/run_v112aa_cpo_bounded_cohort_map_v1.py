from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112aa_cpo_bounded_cohort_map_v1 import (
    V112AACPOBoundedCohortMapAnalyzer,
    load_json_report,
    write_v112aa_cpo_bounded_cohort_map_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AA CPO bounded cohort map.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112AACPOBoundedCohortMapAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112aa_phase_charter_report"])),
        reconstruction_payload=load_json_report(Path(config["paths"]["v112z_reconstruction_report"])),
        adjacent_validation_payload=load_json_report(Path(config["paths"]["v112r_adjacent_validation_report"])),
        adjacent_split_payload=load_json_report(Path(config["paths"]["v112y_adjacent_split_report"])),
        spillover_factor_payload=load_json_report(Path(config["paths"]["v112x_spillover_factor_report"])),
    )
    output_path = write_v112aa_cpo_bounded_cohort_map_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AA bounded cohort map report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
