from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112z_cycle_reconstruction_protocol_v1 import (
    V112ZCycleReconstructionProtocolAnalyzer,
    load_json_report,
    write_v112z_cycle_reconstruction_protocol_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12Z cycle reconstruction protocol.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112ZCycleReconstructionProtocolAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112z_phase_charter_report"])),
        readiness_payload=load_json_report(Path(config["paths"]["v112u_readiness_report"])),
        adjacent_probe_payload=load_json_report(Path(config["paths"]["v112y_probe_report"])),
        spillover_probe_payload=load_json_report(Path(config["paths"]["v112x_probe_report"])),
    )
    output_path = write_v112z_cycle_reconstruction_protocol_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12Z protocol report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
