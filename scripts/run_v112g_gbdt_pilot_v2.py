from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112g_gbdt_pilot_v2 import (
    V112GGBDTPilotV2Analyzer,
    load_json_report,
    write_v112g_gbdt_pilot_v2_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12G GBDT pilot v2.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112GGBDTPilotV2Analyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112g_phase_charter_report"])),
        pilot_dataset_payload=load_json_report(Path(config["paths"]["v112b_pilot_dataset_freeze_report"])),
        baseline_v1_payload=load_json_report(Path(config["paths"]["v112b_baseline_readout_report"])),
        gbdt_v1_payload=load_json_report(Path(config["paths"]["v112d_sidecar_pilot_report"])),
        baseline_v2_payload=load_json_report(Path(config["paths"]["v112g_baseline_readout_v2_report"])),
    )
    output_path = write_v112g_gbdt_pilot_v2_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12G GBDT pilot v2 report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
