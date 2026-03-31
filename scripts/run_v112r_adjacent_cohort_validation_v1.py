from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112r_adjacent_cohort_validation_v1 import (
    V112RAdjacentCohortValidationAnalyzer,
    load_json_report,
    write_v112r_adjacent_cohort_validation_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12R adjacent cohort validation.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112RAdjacentCohortValidationAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112r_phase_charter_report"])),
        registry_payload=load_json_report(Path(config["paths"]["v112p_registry_report"])),
        draft_batch_payload=load_json_report(Path(config["paths"]["v112q_draft_batch_report"])),
    )
    output_path = write_v112r_adjacent_cohort_validation_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12R adjacent cohort validation report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
