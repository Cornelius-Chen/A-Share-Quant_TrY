from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113f_owner_review_guide_v1 import (
    V113FOwnerReviewGuideAnalyzer,
    load_json_report,
    write_v113f_owner_review_guide_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13F owner review guide.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V113FOwnerReviewGuideAnalyzer()
    result = analyzer.analyze(
        pilot_object_pool_payload=load_json_report(Path(config["paths"]["v113f_pilot_object_pool_report"])),
        review_sheet_payload=load_json_report(Path(config["paths"]["v113f_label_review_sheet_report"])),
    )
    output_path = write_v113f_owner_review_guide_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13F owner review guide report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
