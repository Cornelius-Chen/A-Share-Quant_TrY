from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112bx_packaging_process_enabler_balance_band_review_v1 import (
    V112BXPackagingProcessEnablerBalanceBandReviewAnalyzer,
    load_json_report,
    write_v112bx_packaging_process_enabler_balance_band_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BX packaging-process-enabler balance band review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    analyzer = V112BXPackagingProcessEnablerBalanceBandReviewAnalyzer()
    result = analyzer.analyze(
        bw_payload=load_json_report(Path(config["paths"]["bw_report"])),
    )
    output_path = write_v112bx_packaging_process_enabler_balance_band_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BX balance band review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
