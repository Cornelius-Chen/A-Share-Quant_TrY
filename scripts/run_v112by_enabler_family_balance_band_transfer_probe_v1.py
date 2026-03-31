from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112by_enabler_family_balance_band_transfer_probe_v1 import (
    V112BYEnablerFamilyBalanceBandTransferProbeAnalyzer,
    load_json_report,
    write_v112by_enabler_family_balance_band_transfer_probe_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BY enabler-family balance-band transfer probe.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    analyzer = V112BYEnablerFamilyBalanceBandTransferProbeAnalyzer()
    result = analyzer.analyze(
        bx_payload=load_json_report(Path(config["paths"]["bx_report"])),
        bp_payload=load_json_report(Path(config["paths"]["bp_report"])),
        az_payload=load_json_report(Path(config["paths"]["az_report"])),
    )
    output_path = write_v112by_enabler_family_balance_band_transfer_probe_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BY transfer probe report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
