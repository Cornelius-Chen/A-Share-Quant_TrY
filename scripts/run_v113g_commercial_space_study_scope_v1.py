from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113g_commercial_space_study_scope_v1 import (
    V113GCommercialSpaceStudyScopeAnalyzer,
    load_json_report,
    write_v113g_commercial_space_study_scope_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13G commercial-space study scope.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V113GCommercialSpaceStudyScopeAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v113g_phase_charter_report"])),
        pilot_object_pool_payload=load_json_report(Path(config["paths"]["v113f_pilot_object_pool_report"])),
    )
    output_path = write_v113g_commercial_space_study_scope_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13G study scope report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
