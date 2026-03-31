from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112bs_penalized_target_mapping_refinement_v1 import (
    V112BSPenalizedTargetMappingRefinementAnalyzer,
    load_json_report,
    write_v112bs_penalized_target_mapping_refinement_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BS penalized target mapping refinement.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    analyzer = V112BSPenalizedTargetMappingRefinementAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        fusion_pilot_payload=load_json_report(Path(config["paths"]["fusion_pilot_report"])),
        training_layer_payload=load_json_report(Path(config["paths"]["training_layer_report"])),
        cycle_reconstruction_payload=load_json_report(Path(config["paths"]["cycle_reconstruction_report"])),
    )
    output_path = write_v112bs_penalized_target_mapping_refinement_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BS penalized target mapping refinement report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
