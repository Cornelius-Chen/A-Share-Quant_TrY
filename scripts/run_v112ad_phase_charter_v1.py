from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112ad_phase_charter_v1 import (
    V112ADPhaseCharterAnalyzer,
    load_json_report,
    write_v112ad_phase_charter_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AD phase charter.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112ADPhaseCharterAnalyzer()
    result = analyzer.analyze(
        reconstruction_payload=load_json_report(Path(config["paths"]["v112z_reconstruction_report"])),
        cohort_map_payload=load_json_report(Path(config["paths"]["v112aa_cohort_map_report"])),
        unsupervised_probe_payload=load_json_report(Path(config["paths"]["v112ac_probe_report"])),
    )
    output_path = write_v112ad_phase_charter_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AD phase charter report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
