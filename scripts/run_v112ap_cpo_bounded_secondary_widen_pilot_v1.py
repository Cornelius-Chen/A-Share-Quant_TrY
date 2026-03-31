from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112ap_cpo_bounded_secondary_widen_pilot_v1 import (
    V112APCPOBoundedSecondaryWidenPilotAnalyzer,
    write_v112ap_cpo_bounded_secondary_widen_pilot_report,
)
from a_share_quant.strategy.v112ap_phase_charter_v1 import load_json_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AP bounded secondary widen pilot.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112APCPOBoundedSecondaryWidenPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112ap_phase_charter_report"])),
        role_patch_payload=load_json_report(Path(config["paths"]["v112ao_role_patch_report"])),
        dataset_assembly_payload=load_json_report(Path(config["paths"]["v112aj_dataset_report"])),
        binding_review_payload=load_json_report(Path(config["paths"]["v112ak_binding_review_report"])),
        cycle_reconstruction_payload=load_json_report(Path(config["paths"]["v112z_cycle_reconstruction_report"])),
    )
    output_path = write_v112ap_cpo_bounded_secondary_widen_pilot_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AP bounded secondary widen pilot report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
