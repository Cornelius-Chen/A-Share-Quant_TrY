from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112c_baseline_hotspot_review_v1 import (
    V112CBaselineHotspotReviewAnalyzer,
    load_json_report,
    write_v112c_baseline_hotspot_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12C baseline hotspot review.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112CBaselineHotspotReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112c_phase_charter_report"])),
        baseline_readout_payload=load_json_report(Path(config["paths"]["v112b_baseline_readout_report"])),
    )
    output_path = write_v112c_baseline_hotspot_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12C hotspot review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
