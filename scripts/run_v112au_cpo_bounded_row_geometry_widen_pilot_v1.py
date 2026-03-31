from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112au_cpo_bounded_row_geometry_widen_pilot_v1 import (
    V112AUCPOBoundedRowGeometryWidenPilotAnalyzer,
    load_json_report,
    write_v112au_cpo_bounded_row_geometry_widen_pilot_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AU bounded row-geometry widen pilot.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        post_patch_rerun_payload=load_json_report(Path(config["paths"]["v112at_rerun_report"])),
        dataset_assembly_payload=load_json_report(Path(config["paths"]["v112aj_dataset_report"])),
        cycle_reconstruction_payload=load_json_report(Path(config["paths"]["v112z_cycle_report"])),
    )
    output_path = write_v112au_cpo_bounded_row_geometry_widen_pilot_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AU row-geometry widen pilot report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
