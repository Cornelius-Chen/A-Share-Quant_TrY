from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112o_optical_link_study_scope_v1 import (
    V112OOpticalLinkStudyScopeAnalyzer,
    load_json_report,
    write_v112o_optical_link_study_scope_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12O optical-link study scope.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112OOpticalLinkStudyScopeAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112o_phase_charter_report"])),
        pilot_dataset_payload=load_json_report(Path(config["paths"]["v112b_pilot_dataset_report"])),
    )
    output_path = write_v112o_optical_link_study_scope_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12O study scope report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
