from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112bb_cpo_default_10_row_guarded_layer_pilot_v1 import (
    V112BBCPODefault10RowGuardedLayerPilotAnalyzer,
    load_json_report,
    write_v112bb_cpo_default_10_row_guarded_layer_pilot_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BB default 10-row guarded-layer pilot.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112BBCPODefault10RowGuardedLayerPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        training_layer_extension_payload=load_json_report(Path(config["paths"]["v112az_extension_report"])),
        cycle_reconstruction_payload=load_json_report(Path(config["paths"]["v112z_cycle_reconstruction_report"])),
        v112am_pilot_payload=load_json_report(Path(config["paths"]["v112am_pilot_report"])),
        v112ap_pilot_payload=load_json_report(Path(config["paths"]["v112ap_pilot_report"])),
        v112ax_pilot_payload=load_json_report(Path(config["paths"]["v112ax_pilot_report"])),
    )
    output_path = write_v112bb_cpo_default_10_row_guarded_layer_pilot_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BB default 10-row guarded-layer pilot report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
