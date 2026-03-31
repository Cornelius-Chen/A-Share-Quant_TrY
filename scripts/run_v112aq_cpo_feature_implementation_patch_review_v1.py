from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112aq_cpo_feature_implementation_patch_review_v1 import (
    V112AQCPOFeatureImplementationPatchReviewAnalyzer,
    load_json_report,
    write_v112aq_cpo_feature_implementation_patch_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AQ feature implementation patch review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112AQCPOFeatureImplementationPatchReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        readiness_payload=load_json_report(Path(config["paths"]["v112al_readiness_report"])),
        widen_pilot_payload=load_json_report(Path(config["paths"]["v112ap_widen_pilot_report"])),
        daily_board_payload=load_json_report(Path(config["paths"]["v112v_daily_board_report"])),
        future_calendar_payload=load_json_report(Path(config["paths"]["v112w_future_calendar_report"])),
    )
    output_path = write_v112aq_cpo_feature_implementation_patch_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AQ feature implementation patch review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
