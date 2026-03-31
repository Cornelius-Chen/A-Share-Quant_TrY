from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v19_feature_breadth_rereview_v1 import (
    V19FeatureBreadthRereviewAnalyzer,
    load_json_report,
    write_v19_feature_breadth_rereview_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.9 per-feature breadth re-review.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V19FeatureBreadthRereviewAnalyzer()
    result = analyzer.analyze(
        breadth_rereview_protocol_payload=load_json_report(Path(config["paths"]["v19_breadth_rereview_protocol_report"])),
        feature_promotion_gap_review_payload=load_json_report(Path(config["paths"]["v17_feature_promotion_gap_review_report"])),
        screened_collection_payload=load_json_report(Path(config["paths"]["v18c_screened_collection_report"])),
    )
    output_path = write_v19_feature_breadth_rereview_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.9 feature breadth re-review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
