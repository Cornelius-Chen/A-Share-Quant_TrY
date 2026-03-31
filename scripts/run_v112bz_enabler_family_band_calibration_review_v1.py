from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112bz_enabler_family_band_calibration_review_v1 import (
    V112BZEnablerFamilyBandCalibrationReviewAnalyzer,
    load_json_report,
    write_v112bz_enabler_family_band_calibration_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BZ enabler-family band calibration review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    analyzer = V112BZEnablerFamilyBandCalibrationReviewAnalyzer()
    result = analyzer.analyze(
        bx_payload=load_json_report(Path(config["paths"]["bx_report"])),
        bp_payload=load_json_report(Path(config["paths"]["bp_report"])),
        az_payload=load_json_report(Path(config["paths"]["az_report"])),
    )
    output_path = write_v112bz_enabler_family_band_calibration_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BZ calibration review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
