from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112bd_market_regime_overlay_feature_review_v1 import (
    V112BDMarketRegimeOverlayFeatureReviewAnalyzer,
    load_json_report,
    write_v112bd_market_regime_overlay_feature_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BD market regime overlay feature review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112BDMarketRegimeOverlayFeatureReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        v112af_feature_family_payload=load_json_report(Path(config["paths"]["v112af_feature_family_report"])),
        v113c_state_usage_payload=load_json_report(Path(config["paths"]["v113c_state_usage_report"])),
    )
    output_path = write_v112bd_market_regime_overlay_feature_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BD market regime overlay review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
